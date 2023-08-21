import re
from typing import Dict

import torch
from aiogram import types

from transformers import GPT2LMHeadModel, GPT2Tokenizer
from transformers import StoppingCriteria, StoppingCriteriaList


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
    regex = r"[^а-яА-ЯёЁ\s\w\"?!.,:;)(=+-]|\s+(?=[.,!?:;])"

    def get_text(self, message: types.Message) -> bool:
        user_text = re.sub(self.regex, "", message.text, 0, re.MULTILINE).strip()
        if not user_text:
            return False
        if message.reply_to_message.text:
            bot_text = re.sub(self.regex, "", message.reply_to_message.text, 0, re.MULTILINE).strip()
            if bot_text:
                self.all_mesgs.append(f'@@ВТОРОЙ@@ {bot_text} ')
        self.all_mesgs.append(f'@@ПЕРВЫЙ@@ {user_text} ')
        if len(self.all_mesgs) > 10:
            self.all_mesgs = self.all_mesgs[2:]
        return True

    def text(self, message: types.Message):
        good = self.get_text(message)
        if not good:
            return ''
        msgs = "".join(self.all_mesgs)
        text = f'{msgs}@@ВТОРОЙ@@'
        return text


class GPT2TextGenerator:
    # Все буквы, цифры, основные знаки припинания, скобки и ковычки
    regex = r"[^а-яА-ЯёЁ\s\w\"?!.,:;)(=+-]|\s+(?=[.,!?:;])"
    # Возможные окончания генерации
    stop_words = ['.', ' ?', '!', '\n', ' \n', '..', '...', '?', '.?', '!?', '?!', '@', '?)']

    def __init__(self, model_path):
        self.model = GPT2LMHeadModel.from_pretrained(model_path)
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_path)
        self.model.config.pad_token_id = self.model.config.eos_token_id
        # self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.device = torch.device("cpu")
        self.model.to(self.device)
        self.stop_ids = [self.tokenizer.encode(w)[0] for w in self.stop_words]
        self.stop_criteria = KeywordsStoppingCriteria(self.stop_ids)

    def reply2(self, text: str):
        # print(text)
        input_ids = self.tokenizer.encode(
            text,
            add_special_tokens=False,
            return_tensors="pt",
        ).to(self.device)

        out = self.model.generate(
            input_ids,
            max_new_tokens=32,
            do_sample=True,
            no_repeat_ngram_size=2,
            temperature=1.6,
            top_k=20, top_p=0.7,
            repetition_penalty=2.0,
            stopping_criteria=StoppingCriteriaList([self.stop_criteria]),
        )

        otvet = list(map(self.tokenizer.decode, out))[0]
        otvet = otvet.replace(text, '').strip()

        # regexp = "&quot;|&laquo;"
        otvet = re.sub(r"&\w{3,6};", "", otvet, 0, re.MULTILINE)

        # print(repr(otvet))
        return otvet


dialogs: Dict[int, Dialog] = {}
tinkoff_gen = GPT2TextGenerator(model_path='ai/models/ruDialoGPT-trained')
