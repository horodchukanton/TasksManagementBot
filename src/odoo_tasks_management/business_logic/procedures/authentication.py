from typing import Union

from telebot.types import Message

from odoo_tasks_management.business_logic.base.operation import (
    Operation,
    Prompt,
)
from odoo_tasks_management.business_logic.base.procedure import Procedure
from odoo_tasks_management.messenger.telegram import Bot
from odoo_tasks_management.odoo.client import OdooClient
from odoo_tasks_management.persistence.db import DB


class Authentication(Procedure):
    def __init__(self, bot: Bot, db: DB, odoo_client: OdooClient):
        super().__init__(bot)
        self._db = db
        self._bot = bot
        self._odoo_client = odoo_client

        self._context = {}
        self._operation = Operation(
            bot=bot,
            prompts=[
                Prompt(
                    text="Please enter an email you use for Odoo",
                    expects=["text"],
                    handler=self.check_login,
                ),
                Prompt(
                    text="Please check your Odoo inbox"
                    " for the OTP code and paste it here",
                    expects=["text"],
                    handler=self.check_otp,
                ),
            ],
            on_finish=self.save_chat_id_for_current_user,
        )

    def check_login(self, chat_id: Union[int, str], message: Message):
        self._context["chat_id"] = chat_id
        self._context["login"] = message.text

        # users = self._odoo_client.get_users()
        # TODO: check that user with this login exists

        self._context["otp"] = self._generate_otp()
        self._send_inbox_message_with_otp(self._context["login"], self._context["otp"])

        return True

    def check_otp(self, chat_id: Union[int, str], message: Message):
        if message.text != self._context["otp"]:
            self._bot.send_message(chat_id, "Wrong OTP code provided")
            self._operation.abort(chat_id)
            return False

        return True

    def save_chat_id_for_current_user(self, chat_id: Union[int, str]):
        # TODO: Save self._context["chat_id"] for user
        #  with a corresponding self._context["login"]

        self._bot.send_message(
            chat_id, f"You are logged in now, {self._context['login']}!"
        )

    @staticmethod
    def _generate_otp() -> str:
        # TODO: generate random number
        return "123456"

    def _send_inbox_message_with_otp(self, odoo_login: str, otp: str):
        self._odoo_client.send_inbox_message(
            odoo_login, f"Here's you code to log into the Telegram Bot: {otp}"
        )
