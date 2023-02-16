from functools import partial

import telebot

from business_logic.router import Router
from messenger.base import Interface
from settings import Settings


class TelegramInterface(Interface):
    _bot = None

    def __init__(
        self,
        settings: Settings,
        message_router: Router
    ):
        self._bot = telebot.TeleBot(
            token=settings.BOT_TOKEN
        )
        # Pass all messages to the Router
        self._bot.message_handler()(partial(message_router.handle_message, self))

    def run(self):
        self._bot.infinity_polling()

    def send_message(self, chat_id: int, text: str):
        self._bot.send_message(chat_id, text)
