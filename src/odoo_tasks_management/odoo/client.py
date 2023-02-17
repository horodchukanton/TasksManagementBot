import xmlrpc.client
from functools import cached_property
from typing import List

from odoo_tasks_management.persistence.models import User


class OdooClient:
    def __init__(self, url, api_key):
        self.url = url
        self.api_key = api_key

        if not self.url or not self.api_key:
            raise EnvironmentError(
                "Odoo URL and API key have to be specified in config.env"
            )

    @cached_property
    def common(self):
        return xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")

    @cached_property
    def uid(self):
        return self.common.authenticate("", "", self.api_key, {})

    @cached_property
    def models(self):
        return xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")

    def get_users(self) -> List[User]:
        user_ids = self.models.execute_kw(
            self.url,
            self.uid,
            self.api_key,
            "res.users",
            "search",
            [[]],
        )
        users = self.models.execute_kw(
            self.url,
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
        task_id = self.models.execute_kw(
            self.url, self.uid, self.api_key, "crm.task", "create", [{...}]
        )
        return task_id

    def send_inbox_message(self, login, message):
        # TODO
        pass
