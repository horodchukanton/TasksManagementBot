import re
from typing import Union

from sqlalchemy import and_, or_
from telebot import types
from telebot.util import quick_markup

from odoo_tasks_management.business_logic.base.operation import Operation, Prompt, PromptMessage
from odoo_tasks_management.business_logic.base.procedure import Procedure
from odoo_tasks_management.messenger.telegram import Bot
from odoo_tasks_management.persistence.db import DB
from odoo_tasks_management.persistence.models import Project, Task


class CreateTaskMenu(Procedure):
    def __init__(self, router: 'Router', db: DB, bot: Bot):
        super().__init__(bot)
        self._db = db
        self._router = router
        self._operation = Operation(
            bot=bot,
            prompts=[
                Prompt(
                    message=self.show_projects_list,
                    expects=["text"],
                    handler=self.project_chosen,
                ),
                Prompt(
                    message=PromptMessage(
                        text='Введіть заголовок задачі',
                    ),
                    expects=["text"],
                    handler=self.title_name,
                ),
                Prompt(
                    message=PromptMessage(
                        text='Оберіть виконавця задачі',
                    ),
                    expects=["text"],
                    handler=self.title_name,
                ),
            ]
        )

        self._context = {}
    def show_projects_list(self, operation, chat_id):
        bot = operation.bot
        projects = self._get_projects()
        bot.send_message(chat_id, text='Оберіть проект для майбутньої задачі️ 🔽')

        # формуємо markup для кожного словника, який поверне функція self._get_projects(),
        for project in projects:
            project_name = project
            project_id = projects[project]
            markup = quick_markup(
                {project_name: {'callback_data': project_id}},
            )
            bot.send_message(chat_id, text='⇲️', reply_markup=markup)
        return

    def _get_projects(self):
        # знаходимо id проекту, отримуємо масив усіх проектів
        projects_id = self._db.session().query(Project.id).all()

        current_projects_id = []
        for id in projects_id:
            current_projects_id.append(id[0])

        # знаходимо проекти за якими людина керівник
        users_project_names_ids_d = self._db.session().query(
            Project.name, Project.id).filter_by(user_id=35).all()


        #знаходимо задачі в таблиці задач за id поточного користувача, які не скасовані та не виконані
        project_id_for_names_task = self._db.session().query(Task.project_id).filter(
            and_(
                Task.project_id.in_(current_projects_id),
                Task.status != "Виконано",
                Task.status != "Скасовано",
                or_(
                  Task.assignee == 39,
                  Task.responsible == 39,
                )
            )
        ).distinct().all()


        # отримуємо "чистий масив"
        task_projects_ids = []
        for id in project_id_for_names_task:
            task_projects_ids.append(id[0])

        # знаходимо по id проекту його назву в таблиці проектів, добавляємо в масив
        project_names_from_tasks = self._db.session().query(
            Project.name, Project.id
        ).filter(Project.id.in_(task_projects_ids)).all()

        merged_list = list(
            set(project_names_from_tasks + users_project_names_ids_d))

        inline_buttons = {}
        for value in merged_list:
            button_name = f"{value[0]}"
            inline_buttons[button_name] = value[1]
        return inline_buttons

    def project_chosen(self, chat_id, message):
        # завдяки колбеку у відповідній функції, ми отримуємо id з повідомлення
        project_id = message.text

        self._context['project_id'] = project_id

        # знаходимо в таблиці проектів ім'я проекту по іd
        current_project_name = self._db.session().query(Project.name).filter_by(
            id=project_id).one()[0]
        self._bot.send_message(chat_id,
                               f"Обраний проект: {current_project_name}")
        self._context['project'] = current_project_name

    def title_name(self, chat_id, message):
        title_task = message.text
        self._context['title'] = title_task
        self._bot.send_message(chat_id,
                               f"Заголовок задачі: {title_task}")

    def get_users(self):
        users_id = self._db.session().query(Task.id).all()
