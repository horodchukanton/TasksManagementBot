from typing import Union

from telebot import types
from telebot.types import Message

from odoo_tasks_management.business_logic.base.operation import Prompt, \
    Operation
from odoo_tasks_management.business_logic.base.procedure import Procedure
from odoo_tasks_management.messenger.telegram import Bot
from odoo_tasks_management.persistence.db import DB


class RootMenu(Procedure):

    def __init__(self, bot: Bot, db: DB):
        super().__init__(bot)
        self._db = db
        self._operation = Operation(
            bot=bot,
            prompts=[
                Prompt(
                    buttons=[
                        'Мої Проекти', 'Мої Задачі', 'Створити задачу'
                    ],
                    expects=["text"],
                    handler=self.choose_chapter,
                    text='Привіт! Вітаю у Головному меню'
                ),
            ],
            on_finish=lambda x: True,
        )

        self._context = {}

    def choose_chapter(self, chat_id: Union[int, str], message: Message):

        all_projects = ['project1', 'project2', 'project3']
        all_tasks = ['task1', 'task2', 'task3']
        if message.text == "Мої Проекти":

            items = []
            markup = types.ReplyKeyboardMarkup()
            for project in all_projects:
                item = types.KeyboardButton(f'{project}')
                items.append(item)

            markup.row(*items)

            close = types.KeyboardButton("Головне меню")
            markup.add(close)
            self._bot.send_message(
                chat_id,
                "Оберіть який проект бажаєте перевірити",
                reply_markup=markup
            )

        elif message.text == "Мої Задачі":
            items = []
            markup = types.ReplyKeyboardMarkup()
            for task in all_tasks:
                item = types.KeyboardButton(f'{task}')
                items.append(item)
            markup.row(*items)
            close = types.KeyboardButton("Головне меню")
            markup.add(close)
            self._bot.send_message(
                chat_id,
                "Оберіть яку задачу бажаєте переглянути",
                reply_markup=markup
            )
        elif message.text == "Головне меню":
            # Повернення до головної клавіатури
            markup = types.ReplyKeyboardMarkup()
            item1 = types.KeyboardButton("Мої Проекти")
            item2 = types.KeyboardButton("Мої Задачі")
            item3 = types.KeyboardButton("Створити задачу")
            item4 = types.KeyboardButton("Закрити клавіатуру")

            markup.row(item1, item2, item3)
            markup.add(item4)
            self._bot.send_message(
                chat_id,
                "Повернення до головної клавіатури.",
                reply_markup=markup
            )

        for project in all_projects:
            if message.text == f"{project}":
                self._bot.send_message(
                    chat_id,
                    "О, здається тут щось для тебе є!"
                )
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    f'Подивитись проект, {project}',
                    callback_data='button_pressed'
                ))
                self._bot.send_message(
                    chat_id,
                    'Подивитись проект',
                    reply_markup=markup)

        for task in all_tasks:
            if message.text == f"{task}":
                self._bot.send_message(
                    chat_id,
                    "О, здається тут щось для тебе є!"
                )
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    f'Відмітити як виконано, {task}',
                    callback_data='button_pressed'
                ))
                self._bot.send_message(
                    chat_id,
                    'Відмітити як виконано',
                    reply_markup=markup)
