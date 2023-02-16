import xmlrpc.client
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
        #
        # self.common = xmlrpc.client.ServerProxy(
        #     "{}/xmlrpc/2/common".format(self.url)
        # )
        # self.uid = self.common.authenticate("", "", self.api_key, {})
        # self.models = xmlrpc.client.ServerProxy(
        #     "{}/xmlrpc/2/object".format(self.url)
        # )

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
