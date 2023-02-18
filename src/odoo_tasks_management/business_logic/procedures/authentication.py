from typing import Union

import injector
from telebot.types import Message

from odoo_tasks_management.business_logic.base.operation import (
    Operation,
    Prompt,
)
from odoo_tasks_management.messenger.telegram import Bot
from odoo_tasks_management.odoo.client import OdooClient


class AuthenticationFactory:
    @injector.inject
    def __init__(self, odoo_client: OdooClient, bot: Bot):
        self._odoo_client = odoo_client
        self._bot = bot

    def initialize_authentication(self):
        return Authentication(self._odoo_client, self._bot)


class Authentication:
    def __init__(self, odoo_client: OdooClient, bot: Bot):
        self._odoo_client = odoo_client
        self._bot = bot
        self._operation = Operation(
            bot=bot,
            prompts=[
                Prompt(
                    text="Please enter your Odoo login",
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

        self._context = {}

    def run(self, chat_id: Union[str, int]):
        self._operation.run(chat_id)
        return self._operation

    def check_login(self, chat_id: Union[int, str], message: Message):
        self._context["login"] = message.text

        # users = self._odoo_client.get_users()
        # TODO: check that user with this login exists

        self._context["otp"] = "123456"  # TODO: generate random number
        self._odoo_client.send_inbox_message(
            self._context["login"], self._context["otp"]
        )
        # TODO: Send OTP code as an inbox mail for the proposed login
        return True

    def check_otp(self, chat_id: Union[int, str], message: Message):
        if message.text != self._context["otp"]:
            self._bot.send_message(chat_id, "Wrong OTP code provided")
            self._operation.abort(chat_id)
            return False

        return True

    def save_chat_id_for_current_user(self, chat_id: Union[int, str]):
        # TODO: Update the user with a corresponding login

        self._bot.send_message(
            chat_id, f"You are logged in now, {self._context['login']}!"
        )
