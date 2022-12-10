from typing import Dict
from dataclasses import dataclass
from environs import Env

from database.db import Chat

# @dataclass
# class DbConfig:
#     host: str
#     password: str
#     user: str
#     database: str


@dataclass
class AlcoBot:
    token: str
    main_group_id: int
    # admin_ids: list[int]
    # use_redis: bool


# @dataclass
# class Miscellaneous:
#     other_params: str = None


@dataclass
class Config:
    bot: AlcoBot
    # db: DbConfig
    # misc: Miscellaneous


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        bot=AlcoBot(
            token=env.str("BOT_TOKEN"),
            main_group_id=int(env.str("GROUP_BROTHERHOOD"))
            # admin_ids=list(map(int, env.list("ADMINS"))),
            # use_redis=env.bool("USE_REDIS"),
        ),
        # db=DbConfig(
        #     host=env.str('DB_HOST'),
        #     password=env.str('DB_PASS'),
        #     user=env.str('DB_USER'),
        #     database=env.str('DB_NAME')
        # ),
        # misc=Miscellaneous()
    )


# глобальные переменные
data: Dict[int, Chat] = {}  # chat_id: Chat
cats = []
images_drunk = []
images_mem = []
time_ban = 120
# sim_gens = {}
weapons = {}

names = {
    1105830408: ('Кузьмич', 'Кузменков', 'Антон'),
    149303688: ('Сережа', 'Сережка', 'Китаец'),
    815268868: ('Санька', 'Шурик', 'Гриб'),
    176814724: ('Чира', 'Чирков', 'Роман Чирков'),
    290748920: ('Черный', 'Бармин', 'Роман Бармин'),
    304804118: ('Грач', 'Птица', 'Антон', 'Нейротренер'),
    2070208630: ('Алкаш', 'Бот', 'Алкаш-Бот')
}
