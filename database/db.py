import sqlite3
import logging
import time
import json
from typing import Dict

import config as cfg

from math import sqrt, log

file_db = 'sql/hit.db'


class Chat:
    def __init__(self, chat_id):
        self.connection = sqlite3.connect(file_db)
        self.cur = self.connection.cursor()
        with self.connection:
            try:
                config = self.cur.execute('SELECT * FROM config WHERE chat_id = ?', (chat_id,)).fetchall()
            except sqlite3.Error:
                logging.exception('Ошибка при чтении данных из базы для чата db.py')
        if not config:
            self.pikabu_delta = 0
            self.ban_rule = ''
            self.pikabu_posted = []
        else:
            self.pikabu_delta = config[0][1]
            self.ban_rule = config[0][2]
            self.pikabu_posted = json.loads(config[0][3]) if config[0][3] else []

        self.users: Dict[int, User] = {}
        # self.active_polls = {}
        self.id = chat_id
        self.last_msg_time = int(time.time())
        # self.last_dice_time = 0
        self.pikabu_to_post = []
        self.message_counter = 10
        self._time_fight = 0

    @property
    def is_fight_now(self):
        return self._time_fight >= time.time()

    @is_fight_now.setter
    def is_fight_now(self, t):
        self._time_fight = time.time() + t

    def db_config_update(self):
        with self.connection:
            x = self.cur.execute('SELECT * FROM config WHERE chat_id == ?', (self.id,)).fetchall()
            if x:
                try:
                    self.cur.execute(
                        'UPDATE config SET pikabu = ?, pikabu_posted = ? WHERE chat_id = ?',
                        (self.pikabu_delta, json.dumps(self.pikabu_posted[:30]), self.id,))
                except sqlite3.Error:
                    logging.exception('Ошибка обращения к базе config')
            else:
                try:
                    self.cur.execute(
                        'INSERT INTO config (chat_id, pikabu, ban_rule, pikabu_posted) VALUES(?, ?, ?, ?)',
                        (self.id, self.pikabu_delta, self.ban_rule, json.dumps(self.pikabu_posted[:30]),))
                except sqlite3.Error:
                    logging.exception('Ошибка обращения к базе config')


class User:
    class Weapon:
        def __init__(self, sql_str):
            properties = sql_str.split('@')
            if len(properties) < 5:
                properties.append(0)
            self.pic = properties[0]
            self.name = properties[1]
            self.dmg = int(properties[2])
            self.durability = int(properties[3])
            self.for_user_id = int(properties[4])
            self.taked = True

    def __init__(self, user, chat_id):
        self.connection = sqlite3.connect(file_db)
        self.cur = self.connection.cursor()
        user_db = self.get_user(user, chat_id)
        # 	(user_id, chat_id, uebal, poluchil, sebe, name, hp, atack, a_bonus, weapon)
        self.id = user_db[0]
        self.chat_id = user_db[1]
        self.uebal = user_db[2]
        self.name = user_db[5]
        self.__hp = user_db[6]
        self.weapon = self.Weapon(user_db[9])
        self.ban_time = 0
        self.cant_steal = False
        self.option: int = 0

        cfg.data[self.chat_id].users[self.id] = self

    @property
    def atack(self):
        bonus = 1000 if self.weapon.for_user_id == self.id else 0
        return int((10 + self.weapon.dmg) * (1 + self.lvl * 0.05) + bonus)

    @property
    def lvl(self):
        return int(sqrt(self.uebal + 1) + log(self.uebal + 1))

    @property
    def tag(self):
        return f'<a href="tg://user?id={self.id}">{self.name} ⭐️{self.lvl}</a>'

    @property
    def hp(self):
        return self.__hp

    @hp.setter
    def hp(self, new_hp):
        self.__hp = new_hp if new_hp > 0 else 0
        # if self.__hp == 0:
        #     self.ban_time = time.time() + 240

    @property
    def banned(self):
        return self.ban_time > time.time()

    def get_user(self, user, chat_id):
        with self.connection:
            user_db = self.cur.execute(
                'SELECT * FROM stat WHERE user_id = ? AND chat_id = ?', (user.id, chat_id)).fetchall()
            if not user_db:
                try:
                    self.cur.execute(
                        'INSERT INTO stat (user_id, chat_id, name) VALUES(?, ?, ?)', (user.id, chat_id, user.first_name)
                    )
                except sqlite3.Error:
                    logging.exception(f"Ошибка вставки строки по ключу user_id={user.id}, chat_id={chat_id} db.py")
                    return None
                user_db = self.cur.execute(
                    'SELECT * FROM stat WHERE user_id = ? AND chat_id = ?', (user.id, chat_id)).fetchall()
        return user_db[0]

    def update(self):
        weapon_sql_str = f'{self.weapon.pic}@{self.weapon.name}@{self.weapon.dmg}@{self.weapon.durability}@{self.weapon.for_user_id}'
        if self.weapon.durability <= 0:
            weapon_sql_str = '👐@нет@0@0'
        with self.connection:
            try:
                self.cur.execute(
                    'UPDATE stat SET uebal = ?, name = ?, hp = ?, weapon = ? WHERE user_id = ? AND chat_id = ?',
                    (self.uebal, self.name, self.hp, weapon_sql_str, self.id, self.chat_id)
                )
            except sqlite3.Error:
                logging.exception('Ошибка update()')


class DataBase:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cur = self.connection.cursor()

    def get_config(self):
        with self.connection:
            x = self.cur.execute('SELECT * FROM config').fetchall()
        return x

    def user_exists(self, user_id, chat_id):
        with self.connection:
            x = self.cur.execute('SELECT * FROM stat WHERE user_id = ? AND chat_id = ?', (user_id, chat_id)).fetchall()
        return True if x else False

    def add_user(self, user, chat_id):
        with self.connection:
            try:
                self.cur.execute(
                    'INSERT INTO stat (user_id, chat_id, name) VALUES(?, ?, ?)', (user.id, chat_id, user.first_name)
                )
            except sqlite3.Error:
                logging.exception("Ошибка вставки строки")
                print(f'Ошибка вставки строки по ключу user_id={user.id}, chat_id={chat_id} db.py')

    def get_random(self, chat_id, user_id):
        with self.connection:
            x = self.cur.execute(
                'SELECT user_id FROM stat WHERE chat_id = ? AND user_id != ? ORDER BY RANDOM() LIMIT 1',
                (chat_id, user_id)).fetchone()
        return x[0] if x else 2070208630

    def name(self, user, chat_id):
        if not self.user_exists(user.id, chat_id):
            self.add_user(user, chat_id)
        with self.connection:
            try:
                name = self.cur.execute(
                    'SELECT name FROM stat WHERE user_id = ? AND chat_id = ?', (user.id, chat_id)).fetchone()
            except sqlite3.Error:
                logging.exception("Ошибка получения имени")
        return name[0] if name else user.first_name

    # def atack_bonus(self, user_id, chat_id, a_bonus):
    #     with self.connection:
    #         x = self.cur.execute(
    #             'SELECT a_bonus FROM stat WHERE chat_id = ? AND user_id = ?', (chat_id, user_id)).fetchone()
    #         x = x[0]
    #         a_bonus = f'{x} {a_bonus}'
    #         try:
    #             self.cur.execute(
    #                 'UPDATE stat SET a_bonus = ? WHERE user_id = ? AND chat_id = ?', (a_bonus, user_id, chat_id)
    #             )
    #         except sqlite3.Error:
    #             logging.exception("Ошибка обновления a_bonus")

    def update_stat(self, user, chat_id, u=0, p=0, s=0):
        if not self.user_exists(user.id, chat_id):
            self.add_user(user, chat_id)
        with self.connection:
            try:
                self.cur.execute(
                    'UPDATE stat SET uebal = uebal + ?, poluchil = poluchil + ?, sebe = sebe + ? '
                    'WHERE user_id = ? AND chat_id = ?', (u, p, s, user.id, chat_id)
                )
            except sqlite3.Error:
                logging.exception("Ошибка обновления статистики")

    def close(self):
        self.connection.close()


db = DataBase('sql/hit.db')
