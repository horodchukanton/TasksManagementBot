from typing import Union

from telebot.types import Message

from odoo_tasks_management.business_logic.base.operation import Operation, Prompt
from odoo_tasks_management.business_logic.base.procedure import Procedure
from odoo_tasks_management.messenger.telegram import Bot
from odoo_tasks_management.persistence.db import DB
from odoo_tasks_management.persistence.models import Project


class CreateTaskMenu(Procedure):
    def __init__(self, router: 'Router', db: DB, bot: Bot):
        super().__init__(bot)
        self._db = db
        self._router = router
        self._operation = Operation(
            bot=bot,
            prompts=[
                Prompt(
                    buttons=self._get_projects(),
                    expects=["text"],
                    handler=self.project_chosen,
                    text='Задачу для якого проекту бажаєте створити?'
                ),
                Prompt(
                    buttons=self._get_title(),
                    expects=["text"],
                    handler=self.task_title,
                    text='Вкажіть заголовок для нової задачі?'
                ),

            ],
            on_finish=lambda x: True,
        )

        self._context = {}

    def _get_projects(self):
        projects = self._db.session().query(Project).all()
        project_names = []
        for project in projects:
            project_names.append(project.name)

        return project_names

    def project_chosen(self, chat_id, message: Message):
        project_name = message.text
        self._bot.send_message(chat_id, f"Chosen project is: {project_name}")
        self._context['project'] = project_name

    def _get_title(self, chat_id, message: Message):
        project_name = message.text
        self._bot.send_message(chat_id, f"Chosen project is: {project_name}")
        self._context['project'] = project_name

