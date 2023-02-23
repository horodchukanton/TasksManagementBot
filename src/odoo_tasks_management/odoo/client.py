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

    
    def create_task(self,
                    project_name,
                    partner_name,
                    task_name,
                    description,
                    deadline):
            models = models(self)

            # отримати id проекту по його назві
            proj_id = models.execute(self,            
                                    self.database, 
                                    self.uid, 
                                    self.api_key,
                                    'project.project',
                                    'search',
                                    [['name', '=', project_name]] )
            proj_id = proj_id[0] #  list to int

            # отримати id клієнта по його імені
            part_id = models.execute_kw(self.database,
                                        self.uid,
                                        self.api_key,
                                        'res.partner',
                                        'search',
                                        [[['name', '=', partner_name]]],
                                        {})
            part_id = part_id[0] #  list to int

            # необхідні поля для нової таски
            fields = {
                        'name': task_name,              # char, назва задачі
                        'project_id': proj_id,          # int, зв'язок з 'project.project'
                        'description': description,     # html
                        'stage_id':0,                   # int4, Тут Є питання !. Зв'язок з 'project.task.type'. Індексація з 0. 
                        'partner_id': part_id,          # int, Клієнт, зв'язок з 'res.partner'
                    'date_deadline': deadline           # YYYY-MM-DD
                    }

            new_task = models.execute_kw(self.database,
                                        self.uid,
                                        self.api_key,
                                        'project.task',
                                        'create',
                                        [fields])
            return new_task # id new task




    def send_inbox_message(self, login, message):
        # TODO
        pass


    def get_all_projects(self, is_active = True):
        models = models(self)

        all_projects_fields = {'fields':['name',
                                        'partner_id',   #  Клієнт
                                        'user_id',      #  Керівник
                                        'create_date',
                                        'description'
                                        ]}

        
        all_projects = models.execute_kw(self.database,
                                            self.uid,
                                            self.api_key,
                                            'project.project',
                                            'search_read',
                                            [[['active', '=', is_active]]],
                                            all_projects_fields) 
        return all_projects

