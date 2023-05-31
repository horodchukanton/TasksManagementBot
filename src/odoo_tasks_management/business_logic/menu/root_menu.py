from typing import Union

from telebot.types import Message

from odoo_tasks_management.business_logic.base.operation import (Operation, Prompt, PromptMessage)
from odoo_tasks_management.business_logic.base.procedure import Procedure
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
                    message=PromptMessage(
                        text='Привіт! Вітаю у Головному меню',
                        buttons=['Мої Задачі', 'Створити задачу']
                    ),
                    expects=["text"],
                    handler=self.choose_chapter,
                ),
            ],
            on_finish=self._goto_chosen_chapter,
        )

        self._context = {}

    def choose_chapter(self, chat_id: Union[int, str], message: Message):
        self._context['chosen'] = message.text

    def _goto_chosen_chapter(self, chat_id):
        if self._context['chosen'] == "Мої Задачі":
            self._router.goto_projects_menu(chat_id, self._bot)
        elif self._context['chosen'] == "Створити задачу":
            self._router.goto_create_task_menu(chat_id, self._bot)
            # self._bot.send_message(
            #     chat_id,
            #     "Ще не готово, зачекайте трошечки"
            # )