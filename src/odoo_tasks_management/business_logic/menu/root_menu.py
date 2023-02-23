from typing import Union

from telebot import types
from telebot.types import Message

from odoo_tasks_management.business_logic.base.operation import (Operation, Prompt)
from odoo_tasks_management.business_logic.base.procedure import Procedure
from odoo_tasks_management.business_logic.menu.projects_menu import ProjectsMenu
from odoo_tasks_management.messenger.telegram import Bot
from odoo_tasks_management.persistence.db import DB


class RootMenu(Procedure):

    def __init__(self, router: 'Router', bot: Bot, db: DB):
        super().__init__(bot)
        self._router = router
        self._db = db
        self._operation = Operation(
            bot=bot,
            prompts=[
                Prompt(
                    buttons=[
                        'Мої Задачі', 'Створити задачу'
                    ],
                    expects=["text", 'image', 'file.txt'],
                    handler=self.choose_chapter,
                    text='Привіт! Вітаю у Головному меню'
                ),
            ],
            on_finish=lambda x: True,
        )

        self._context = {}

    def choose_chapter(self, chat_id: Union[int, str], message: Message):
        if message.text == "Мої Задачі":
            self._router.proceed_with_procedure(
                chat_id,
                ProjectsMenu(self._router, self._db, self._operation.bot)
            )

        elif message.text == 'Створити задачу':
            # Повернення до головної клавіатури
            markup = types.ReplyKeyboardMarkup()
            item1 = types.KeyboardButton("Мої Задачі")
            item2 = types.KeyboardButton("Створити задачу")
            item3 = types.KeyboardButton("Закрити клавіатуру")

            markup.row(item1, item2)
            markup.add(item3)
            self._bot.send_message(
                chat_id,
                "Вітаю у головному меню!",
                reply_markup=markup
            )

