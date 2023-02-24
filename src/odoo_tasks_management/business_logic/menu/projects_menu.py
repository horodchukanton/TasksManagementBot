from typing import Union

from telebot.types import Message

from odoo_tasks_management.business_logic.base.operation import Operation, Prompt
from odoo_tasks_management.business_logic.base.procedure import Procedure
from odoo_tasks_management.messenger.telegram import Bot
from odoo_tasks_management.persistence.db import DB


class ProjectsMenu(Procedure):

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
                    text='За яким проектом бажаєте переглянути задачі'
                ),
            ],
            on_finish=self.start_tasks_for_project_menu,
        )

        self._context = {}

    def _get_projects(self):
        # TODO: get actual projects from DB
        # projects = self._db.session().query(Project).all()
        return ["project1", "project2", "project3", "project4"]

    def project_chosen(self, chat_id, message: Message):
        project_name = message.text
        self._bot.send_message(chat_id, f"Chosen project is: {project_name}")
        self._context['project'] = project_name

    def start_tasks_for_project_menu(self, chat_id: Union[int, str]):
        self._router.goto_tasks_for_project_menu(
            chat_id,
            self._bot,
            self._context['project']
        )
