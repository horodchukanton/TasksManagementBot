import re
from typing import Union

from sqlalchemy import and_
from telebot.types import Message

from odoo_tasks_management.business_logic.base.operation import Operation, Prompt, PromptMessage
from odoo_tasks_management.business_logic.base.procedure import Procedure
from odoo_tasks_management.messenger.telegram import Bot
from odoo_tasks_management.persistence.db import DB
from odoo_tasks_management.persistence.models import Project, Task


class ProjectsMenu(Procedure):

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
                        buttons=self._get_tasks,
                        text="choose task"
                    ),
                    expects=["text"],
                    handler=self.task_chosen,
                    text="Оберіть задачу"
                ),
                Prompt(
                    message=PromptMessage(
                        buttons=["Відмітити задачу, як виконану", "Головне меню"],
                        text='Що ви хочете зробити із задачею?',
                    ),
                    expects=["text"],
                    handler=self.chosen_process_with_tasks,
                ),
            ]
        )

        self._context = {}

    def show_projects_list(self, operation, chat_id):
        bot = operation.bot

        projects = self._get_projects()

        for project_name in projects:
            bot.send_message(chat_id, project_name)

        return

    def _get_projects(self):
        # знаходимо id проекту
        projects_id = self._db.session().query(Project.id).all()
        current_projects_id = []

        # позбуваємось дивних знаків та отримуємо "чистий масив"
        for id in projects_id:
            current_projects_id.append(id[0])

        # знаходимо по id проекту задачі в таблиці Tasks
        project_id_for_names = self._db.session().query(Task.project_id).filter(
            and_(
                Task.project_id.in_(current_projects_id),
                Task.status != "Виконано",
                Task.assignee == 47
            )
        ).distinct().all()

        # позбуваємось дивних знаків та отримуємо "чистий масив"
        task_projects_ids = []
        for id in project_id_for_names:
            task_projects_ids.append(id[0])

        # знаходимо по id в таблиці проектів назву відповідного проекту, добавляємо в масив
        project_names = self._db.session().query(Project.name, Project.id).filter(
            Project.id.in_(task_projects_ids)
        ).all()

        # позбуваємос дивних знаків та отримуємо "чистий масив"
        project_names_ = []
        for id in project_names:
            project_names_.append(id[0])

        inline_buttons = {}

        for value in project_names:
            button_name = f"{value[0]}"
            callback_data = value[1]
            inline_buttons[button_name] = {'callback_data': callback_data}
        print(inline_buttons)
        return inline_buttons

    def project_chosen(self, chat_id, message):
        project_id = message.text
        self._context['project_id'] = project_id

        current_project_name = self._db.session().query(Project.name).filter(
            Project.id == project_id).one()[0]

        project_tasks = self._db.session().query(Task.title).where(
            (Task.project_id == project_id) & (
                    Task.status != "Виконано")).all()
        self._bot.send_message(chat_id, f"Обраний проект: {current_project_name}")
        self._context['project'] = current_project_name

        current_project_tasks = []
        if not project_tasks:
            self._bot.send_message(chat_id, f"За обраним проектом задач не найдено")
            self._router.goto_root_menu(chat_id, self._bot)
            self._operation.is_finished = True
        else:
            for task in project_tasks:
                current_project_tasks.append(task[0])
        self._context['tasks'] = current_project_tasks

    def _get_tasks(self):
        current_project_tasks = self._context['tasks']
        return current_project_tasks

    def task_chosen(self, chat_id, message):
        task_title = message.text
        if task_title not in self._context['tasks']:
            self._bot.send_message(
                chat_id, "Введено неочікуваний текст"
            )
            self._router.goto_root_menu(chat_id, self._bot)

        current_project_id = self._context['project_id']
        task = self._db.session().query(Task).filter(
            and_(
                Task.title == task_title,
                Task.project_id == current_project_id
            )).one()

        task_assignee = task.assignee_user.login
        task_responsible = task.responsible_user.login
        task_deadline = task.deadline
        task_status = task.status
        task_description = self._clean_html_tags(task.description)
        task_planned_hours = task.planned_hours

        self._bot.send_message(
            chat_id,
            f"<b>Заголовок задачі</b>: {task_title}\n"
            f"<b>Виконавець задачі</b>:{task_assignee}\n"
            f"<b>Відповідальний за задачу</b>:{task_responsible}\n"
            f"<b>Кінцевий термін виконання задачі</b>:{task_deadline}\n"
            f"<b>Статус задачі</b>: {task_status}\n"
            f"<b>Опис задачі</b>: {task_description}\n"
            f"<b>Кількість годин для виконання задачі</b>:{task_planned_hours}",
            parse_mode='HTML'
        )
        self._context['task'] = task_title

    def chosen_process_with_tasks(self, chat_id: Union[int, str], message):
        if message.text == "Відмітити задачу, як виконану":
            task_title = self._context['task']
            session = self._db.session()
            task = session.query(Task).filter(
                and_(
                    Task.title == task_title,
                    Task.project_id == self._context['project_id']
                )).one()
            task.status = 'Виконано'
            session.flush()
            session.commit()
            self._bot.send_message(chat_id,
                                   f"<b>{task_title}</b> статус <b>Виконано</b>",
                                   parse_mode='HTML')

            self._router.goto_root_menu(chat_id, self._bot)

        elif message.text == "Головне меню":
            self._router.goto_root_menu(chat_id, self._bot)

    # def start_create_tasks_menu(self, chat_id: Union[int, str]):
    #     self._router.goto_tasks_for_project_menu(
    #         chat_id,
    #         self._bot,
    #         self._context['project']
    #     )
    @staticmethod
    def _clean_html_tags(description):
        pattern = re.compile('<.*?>')
        return re.sub(pattern, '', description)
