import xmlrpc.client
from functools import cached_property
from typing import List

from odoo_tasks_management.persistence.models import User
from odoo_tasks_management.settings import Settings


class OdooClient:
    # This class represents an Odoo XML-RPC client. It is used to communicate with an Odoo
    # instance through the XML-RPC API.

    def __init__(self, settings: Settings):
        # This method is the constructor of the OdooClient class. It takes a 'Settings' object as
        # a parameter and sets several instance variables.

        self.url = settings.ODOO_URL
        # This line sets the 'url' instance variable to the value of the 'ODOO_URL' setting from
        # the 'Settings' object.

        self.database = settings.ODOO_DATABASE
        # This line sets the 'database' instance variable to the value of the 'ODOO_DATABASE'
        # setting from the 'Settings' object.

        self.api_login = settings.ODOO_API_LOGIN
        # This line sets the 'api_login' instance variable to the value of the 'ODOO_API_LOGIN'
        # setting from the 'Settings' object.

        self.api_key = settings.ODOO_API_KEY
        # This line sets the 'api_key' instance variable to the value of the 'ODOO_API_KEY'
        # setting from the 'Settings' object.

        if not self.url or not self.api_key:
            # This line checks whether the 'url' and 'api_key' instance variables are set.
            # If either of them is not set, it raises an 'EnvironmentError' with an error message.

            raise EnvironmentError(
                "ODOO_URL and ODOO_API_KEY have to be specified in config.env"
            )

    @cached_property
    def common(self):
        # This is a property method that returns a cached value of the Odoo XML-RPC common service.
        # The 'cached_property' decorator is used to create a cached property.
        # This means that the property is calculated only once and then stored as an instance
        # variable.

        return xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        # This line creates a new instance of the 'ServerProxy' class from the 'xmlrpc.client'
        # module.
        # The URL of the Odoo XML-RPC common service is constructed using the 'url' instance
        # variable.
        # The 'ServerProxy' object is returned as the value of the 'common' property.

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
