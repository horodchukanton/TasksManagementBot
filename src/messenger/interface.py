from functools import partial

from business_logic.router import Router
from messenger.telegram import Bot


class Interface:
    _bot = None

    def __init__(
        self,
        bot: Bot,
        message_router: Router
    ):
        self._bot = bot
        self._bot.setup_handler(
            message_router.handle_message
        )

    def run(self):
        self._bot.run()

    def send_message(self, chat_id: int, text: str):
        self._bot.send_message(chat_id, text)
