import random
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
from odoo_tasks_management.persistence.models import User


class Authentication(Procedure):
    def __init__(self, router: 'Router', bot: Bot, db: DB, odoo_client: OdooClient):
        super().__init__(bot)
        self._router = router
        self._db = db
        self._bot = bot
        self._odoo_client = odoo_client

        self._context = {}
        self._operation = Operation(
            bot=bot,
            prompts=[
                Prompt(
                    message="Вітаю, вкажіть email, з яким ви зареєстровані в Odoo",
                    expects=["text"],
                    handler=self.check_login,
                ),
                Prompt(
                    message=(
                        "Я відправив Вам одноразовий код у чат Odoo (Telegram Bot Notifications)."
                        " Будь ласка введіть цей код."
                    ),
                    expects=["text"],
                    handler=self.check_otp,
                ),
            ],
            on_finish=self.save_chat_id_for_current_user,
        )

    def check_login(self, chat_id: Union[int, str], message: Message):
        self._context["chat_id"] = chat_id
        self._context["login"] = message.text

        find_user = self._db.session().query(User).filter(
            User.email == self._context["login"]
        ).one_or_none()

        if not find_user:
            return self._operation.abort(
                chat_id, "Користувача з таким email не знайдено"
            )

        self._context["otp"] = self._generate_otp()
        self._send_inbox_message_with_otp(self._context["login"], self._context["otp"])

    def check_otp(self, chat_id: Union[int, str], message: Message):
        if message.text != self._context["otp"]:
            self._operation.abort(chat_id, "Введено невірний код, спробуйте ще раз")

    def save_chat_id_for_current_user(self, chat_id: Union[int, str]):
        session = self._db.session()
        find_user = session.query(User).filter(
            User.email == self._context["login"]
        ).one()
        find_user.telegram_chat_id = chat_id
        session.flush()

        self._bot.send_message(
            chat_id, f"Вітаємо в чаті, {find_user.name}"
        )
        self._router.goto_root_menu(chat_id, self._bot)

    @staticmethod
    def _generate_otp() -> str:
        random_list = []
        for i in range(0, 5):
            n = random.randint(0, 9)
            random_list.append(str(n))
        return ''.join(random_list)

    def _send_inbox_message_with_otp(self, odoo_login: str, otp: str):
        self._odoo_client.send_inbox_message(
            odoo_login, f"{otp} - Вкажіть цей код для авторизації в телеграм боті"
        )
