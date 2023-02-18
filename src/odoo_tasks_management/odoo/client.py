import xmlrpc.client
from functools import cached_property
from typing import List

from odoo_tasks_management.persistence.models import User
from odoo_tasks_management.settings import Settings


class OdooClient:
    def __init__(self, settings: Settings):
        self.url = settings.ODOO_URL
        self.database = settings.ODOO_DATABASE
        self.api_login = settings.ODOO_API_LOGIN
        self.api_key = settings.ODOO_API_KEY

        if not self.url or not self.api_key:
            raise EnvironmentError(
                "ODOO_URL and ODOO_API_KEY have to be specified in config.env"
            )

    @cached_property
    def common(self):
        return xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")

    @cached_property
    def uid(self):
        return self.common.authenticate(
            self.database, self.api_login, self.api_key, {}
        )

    @cached_property
    def models(self):
        return xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")

    def get_users(self) -> List[User]:
        user_ids = self.models.execute_kw(
            self.database,
            self.uid,
            self.api_key,
            "res.users",
            "search",
            [[]],
        )
        users = self.models.execute_kw(
            self.database,
            self.uid,
            self.api_key,
            "res.users",
            "read",
            [user_ids],
            {"fields": ["id", "name", "login", "email"]},
        )
        return users

    def create_task(
        self,
    ):
        # TODO
        pass

    def send_inbox_message(self, login, message):
        # TODO
        pass
