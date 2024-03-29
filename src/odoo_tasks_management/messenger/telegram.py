from functools import partial
from typing import Callable

import injector
import telebot

from odoo_tasks_management.settings import Settings


class Bot:
    @injector.inject
    def __init__(self, settings: Settings):
        self._bot = telebot.TeleBot(token=settings.BOT_TOKEN)

    def run(self):
        self._bot.infinity_polling()

    def send_message(self, chat_id: int, text: str, **kwargs):
        self._bot.send_message(chat_id, text, **kwargs)

    def setup_handler(self, handler: Callable):
        self._bot.callback_query_handler(lambda x: True)(partial(handler, self))
        self._bot.message_handler()(partial(handler, self))
