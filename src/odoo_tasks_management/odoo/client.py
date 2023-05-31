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
        return self.common.authenticate(self.database, self.api_login, self.api_key, {})

    @cached_property
    def models(self):
        return xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")

    def get_users(self) -> List[User]:
        users = self.models.execute_kw(
            self.database,
            self.uid,
            self.api_key,
            "res.users",
            "search_read",
            [[('active', '=', True)]],
            {
                "fields": [
                    "id",
                    "login",
                    "partner_id"
                ]
            }
        )

        return users

    def create_task(self, project_id, task_name, description, deadline, responsible_id, assignee_id, planned_hours, partner_id):


        # # отримати id клієнта по його імені
        # part_id = self.models.execute_kw(
        #     self.database,
        #     self.uid,
        #     self.api_key,
        #     "res.partner",
        #     "search",
        #     [[["name", "=", partner_name]]],
        #     {},
        # )
        # part_id = part_id[0]  # list to int

        # необхідні поля для нової таски
        fields = {
            "name": task_name,  # char, назва задачі
            "project_id": int(project_id),  # int, зв'язок з 'project.project'
            "description": description,  # html
            "stage_id": 0,  # int4, Тут Є питання !. Зв'язок з 'project.task.type'. Індексація з 0.
            "date_deadline": deadline,  # YYYY-MM-DD
            "create_uid": responsible_id,
            "user_id": int(assignee_id),
            "planned_hours": planned_hours,
            "kanban_state": 'normal',
            "partner_id": partner_id,  # int, Клієнт, зв'язок з 'res.partner'
        }

        new_task = self.models.execute_kw(
            self.database, self.uid, self.api_key, "project.task", "create", [fields]
        )
        return new_task  # id new task

    def get_all_projects(self, is_active=True):
        all_projects = self.models.execute_kw(
            self.database,
            self.uid,
            self.api_key,
            "project.project",
            "search_read",
            [[["active", "=", is_active]]],
            {
                "fields": [
                    "name",
                    "partner_id",  # Клієнт
                    "user_id",  # Керівник
                    "create_date",
                    "description",

                ]
            },
        )
        return all_projects

    def get_all_tasks(self):
        all_projects_fields = {
            "fields": [
                "id",
                "project_id",
                "parent_id",
                "user_id",
                # "partner_id",
                "name",
                "description",
                "date_deadline",
                "stage_id",
                "planned_hours",
                "create_uid"
            ]
        }

        all_tasks = self.models.execute_kw(
            self.database,
            self.uid,
            self.api_key,
            "project.task",
            "search_read",
            [[]],
            all_projects_fields,
        )

        return all_tasks

    def send_inbox_message(self, login, message):
        channel_id = self.get_channel_id()
        partner_id = self.find_partner_id_for_user(login)

        notification_ids = [
            (0, 0, {'res_partner_id': partner_id, 'notification_type': 'inbox'})
        ]

        fields = {
            # 'id': channel_id,
            'author_id': 3,
            'body': message,
            'message_type': 'notification',
            'subtype_xmlid': "mail.mt_comment",
            'notification_ids': notification_ids,
            'partner_ids': [partner_id],
            'notify_by_email': False,
        }

        return self.models.execute_kw(
            self.database, self.uid, self.api_key, "mail.channel", "message_post",
            [channel_id],
            fields
        )

    def find_partner_id_for_user(self, login):
        partner_id = self.models.execute(
            self.database,
            self.uid,
            self.api_key,
            "res.partner",
            "search",
            [["email", "=", login]],
        )
        if partner_id:
            return partner_id[0]

        return None

    def get_channel_id(self):
        # Search for channel
        channel_name = "WEBA Telegram bot notifications"
        channel_id = self.models.execute(
            self.database,
            self.uid,
            self.api_key,
            "mail.channel",
            "search",
            [["name", "=", channel_name]],
        )
        if channel_id:
            return channel_id[0]

        # Create new channel
        return self.models.execute_kw(
            self.database, self.uid, self.api_key, "mail.channel", "create", [{
                "name": channel_name,
                "description": "Telegram bot internal notifications",
                "public": "groups",
            }]
        )
