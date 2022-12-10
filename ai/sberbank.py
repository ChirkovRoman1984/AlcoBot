import re
from typing import Dict

import torch
from aiogram import types

from transformers import GPT2LMHeadModel, GPT2Tokenizer
from transformers import StoppingCriteria, StoppingCriteriaList
from rusenttokenize import ru_sent_tokenize


class KeywordsStoppingCriteria(StoppingCriteria):

    def __init__(self, keywords_ids: list):
        self.keywords = keywords_ids

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        if input_ids[0][-1] in self.keywords:
            return True
        return False


class Dialog:
    # Список всех сообщений
    all_mesgs = []
    # # Список сообщений юзера
    # user_msgs = []
    # # Списмок сообщений бота
    # bot_msgs = []
    # Все буквы, цифры, основные знаки припинания, скобки и ковычки
    regex = r"[^а-яА-ЯёЁ\s\w\"?!.,:;)(=+-]|\s+(?=[.,!?:;])"
    #
    # def __init__(self, message: types.Message):
    #     self.chat_id = message.chat.id
    #     user_text = re.sub(self.regex, "", message.text, 0, re.MULTILINE).strip()
    #     self.user_msgs.append(user_text)
    #     bot_text = re.sub(self.regex, "", message.reply_to_message.text, 0, re.MULTILINE).strip()
    #     self.bot_msgs.append(bot_text)

    def get_text(self, message: types.Message) -> bool:
        user_text = re.sub(self.regex, "", message.text, 0, re.MULTILINE).strip()
        if not user_text:
            return False
        if message.reply_to_message.text:
            bot_text = re.sub(self.regex, "", message.reply_to_message.text, 0, re.MULTILINE).strip()
            if bot_text:
                self.all_mesgs.append(f'- {bot_text}')
        self.all_mesgs.append(f'- {user_text}')
        if len(self.all_mesgs) > 10:
            self.all_mesgs = self.all_mesgs[2:]
        return True

    def text(self, message: types.Message):
        good = self.get_text(message)
        if not good:
            return ''
        msgs = "\n".join(self.all_mesgs)
        text = f'История чата:\n{msgs}\n-'
        print(text)
        return text


class GPT2TextGenerator:
    # Все буквы, цифры, основные знаки припинания, скобки и ковычки
    regex = r"[^а-яА-ЯёЁ\s\w\"?!.,:;)(=+-]|\s+(?=[.,!?:;])"
    # Возможные окончания генерации
    stop_words = ['.', ' ?', '!', '\n', ' \n', '..', '...', '?', '.?', '!?', '?!']

    def __init__(self, model_path):
        self.model = GPT2LMHeadModel.from_pretrained(model_path)
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_path)
        self.model.config.pad_token_id = self.model.config.eos_token_id
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.stop_ids = [self.tokenizer.encode(w)[0] for w in self.stop_words]
        self.stop_criteria = KeywordsStoppingCriteria(self.stop_ids)

    def simple_generate(self, text, **kwargs):

        input_ids = self.tokenizer.encode(
            text,
            add_special_tokens=False,
            return_tensors="pt",
        ).to(self.device)

        out = self.model.generate(
            input_ids,
            no_repeat_ngram_size=2,
            repetition_penalty=3.0,
            num_beams=10,
            do_sample=True,
            stopping_criteria=StoppingCriteriaList([self.stop_criteria]),
            **kwargs
        )

        generated = list(map(self.tokenizer.decode, out))[0]
        # regexp = "&quot;|&laquo;"
        generated = re.sub(r"&\w{3,6};", "", generated, 0, re.MULTILINE)
        return generated

    def reply(self, message: types.Message):
        bot_text = ''
        user_text = re.sub(self.regex, "", message.text, 0, re.MULTILINE).strip()
        if not user_text:
            return None
        if message.reply_to_message.text:
            bot_text = re.sub(self.regex, "", message.reply_to_message.text, 0, re.MULTILINE).strip()
        if bot_text:
            text = f'История чата:\n - {bot_text}\n - {user_text}\n -'
        else:
            text = f'- {user_text}\n -'

        input_ids = self.tokenizer.encode(
            text,
            add_special_tokens=False,
            return_tensors="pt",
        ).to(self.device)

        if len(input_ids[0]) > 512:
            return 'Я столько читать не умею...'

        out = self.model.generate(
            input_ids,
            max_new_tokens=24,
            no_repeat_ngram_size=2,
            temperature=2.0,
            top_k=20, top_p=0.7,
            # length_penalty меньше ноля для более коротких генераций used with beam-based generation
            # length_penalty=-1.0,
            # штраф за повторения, хз как работает
            repetition_penalty=2.0,
            # num_beams=10,
            # early_stopping=True,
            # do_sample=True,
            # Температура является мерой креативности модели: чем выше температура,
            # тем более «творческой» будет реакция модели.
            # Штраф за повторение опять же говорит сам за себя — чем выше это значение,
            # тем больше будет штрафовать модель за повторение слов.
            stopping_criteria=StoppingCriteriaList([self.stop_criteria]),
        )

        otvet = list(map(self.tokenizer.decode, out))[0]
        otvet = otvet.replace(text, '').strip()
        # regexp = "&quot;|&laquo;"
        otvet = re.sub(r"&\w{3,6};", "", otvet, 0, re.MULTILINE)
        print(repr(otvet))
        if out[0][-1] not in self.stop_ids:
            print('плохой конец')
            otvet = self.text_postprocess(otvet)
        return otvet

    def reply2(self, text: str):
        input_ids = self.tokenizer.encode(
            text,
            add_special_tokens=False,
            return_tensors="pt",
        ).to(self.device)

        out = self.model.generate(
            input_ids,
            max_new_tokens=24,
            no_repeat_ngram_size=2,
            temperature=2.0,
            top_k=20, top_p=0.7,
            repetition_penalty=2.0,
            stopping_criteria=StoppingCriteriaList([self.stop_criteria]),
        )

        otvet = list(map(self.tokenizer.decode, out))[0]
        otvet = otvet.replace(text, '').strip()

        # regexp = "&quot;|&laquo;"
        otvet = re.sub(r"&\w{3,6};", "", otvet, 0, re.MULTILINE)

        print(repr(otvet))
        return otvet

    def text_preprocess(self, message: types.Message):
        text = re.sub(self.regex, "", message.text, 0, re.MULTILINE)
        if not text:
            return ''
        text = text.strip()
        if text[-1] not in '!?.':
            text += '.'
        return text

    def answer(self, message: types.Message):
        text = self.text_preprocess(message)
        if not text:
            return ''
        input_ids = self.tokenizer.encode(
            text,
            add_special_tokens=False,
            return_tensors="pt",
        ).to(self.device)

        out = self.model.generate(
            input_ids,
            max_new_tokens=24,
            no_repeat_ngram_size=2,
            temperature=1.5,
            repetition_penalty=3.0,
            do_sample=True,
        )

        answer = list(map(self.tokenizer.decode, out))[0]
        answer = answer.replace(text, '')
        answer = self.text_postprocess(answer)
        return answer

    def text_postprocess(self, text):

        # Удаление всяких '&\quot'
        text = re.sub(r"&\w{3,6};", "", text, 0, re.MULTILINE)
        sent_list = text.split('\n')
        if len(sent_list) > 1:
            sent_list = sent_list[:-1]
            text = '\n'.join(sent_list)
            return text

        # Разделение на предложения, и удаление последнего незаконченного
        sent_list = ru_sent_tokenize(text)
        if len(sent_list) > 1:
            sent_list = sent_list[:-1]
            text = ' '.join(sent_list)
            return text

        letters = list(text)
        stop = False
        while not stop:
            letters = letters[:-1]
            if len(letters) == 0:
                stop = True
            elif letters[-1] == '.':
                stop = True
            elif ''.join(letters[-2:]) in ('!)', '?)', '))', ':)', '.)'):
                stop = True
        text = ''.join(letters)
        print(text)
        return text


dialogs: Dict[int, Dialog] = {}
text_gen = GPT2TextGenerator(model_path='ai/models/001')
