from typing import Union

from odoo_tasks_management.business_logic.base.operation import Operation, \
    Prompt
from odoo_tasks_management.business_logic.base.procedure import Procedure
from odoo_tasks_management.messenger.telegram import Bot
from odoo_tasks_management.persistence.db import DB
from odoo_tasks_management.persistence.models import Task, Project, User


class TasksForProjectMenu(Procedure):
    def __init__(self, db: DB, router: 'Router', bot: Bot, project_name: str):
        super().__init__(bot)
        self._db = db
        self._router = router
        self.project_name = project_name
        self._operation = Operation(
            bot=bot,
            prompts=[
                Prompt(
                    buttons=self._get_tasks(project_name),
                    expects=["text"],
                    handler=self.task_chosen,
                    text="choose task"
                ),
                Prompt(
                    expects=["text"],
                    handler=self.chosen_process_with_tasks,
                    text='Що ви хочете зробити із задачею?',
                    buttons=[
                        "Відмітити задачу, як виконану",
                        "Головне меню", ]
                ),
            ],
            on_finish=lambda x: True
        )

        self._context = {}

    def _get_tasks(self, project_name):
        current_project_id = self._db.session().query(Project.id).filter(
            Project.name == project_name).one()[0]
        project_tasks = self._db.session().query(Task.title).where(
            Task.project_id == current_project_id).all()
        current_project_tasks = []
        for task in project_tasks:
            current_project_tasks.append(task[0])
        return current_project_tasks

    def task_chosen(self, chat_id, message):
        chosen_task = message.text
        self._context['task'] = chosen_task
        task_title = chosen_task

        task = self._db.session().query(Task).filter_by(
            title=task_title
        ).one()
        task_assignee = task.assignee_user.login
        task_responsible = task.responsible_user.login
        task_deadline = task.deadline
        task_status = task.status
        task_description = task.description
        task_planned_hours = task.planned_hours

        self._bot.send_message(
            chat_id,
            f"<b>Заголовок задачі</b>: {chosen_task}\n"
            f"<b>Виконавець задачі</b>:{task_assignee}\n"
            f"<b>Відповідальний за задачу</b>:{task_responsible}\n"
            f"<b>Кінцевий термін виконання задачі</b>:{task_deadline}\n"
            f"<b>Статус задачі</b>: {task_status}\n"
            f"<b>Опис задачі</b>: {task_description}\n"
            f"<b>Кількість годин для виконання задачі</b>:{task_planned_hours}",
            parse_mode='HTML'
        )

    def chosen_process_with_tasks(self, chat_id: Union[int, str], message):
        if message.text == "Відмітити задачу, як виконану":
            mark_task = message.text
            self._bot.send_message(chat_id,
                                   f"Process with task is: {mark_task}")

            # Антон: Переходимо у наступне меню
            self._router.goto_mark_task_completed(chat_id, self._bot, self._context['task'])
        elif message.text == "Ознайомитись із описом":
            task_description = message.text
            # TODO: по ID витягнути з БД опис обов'язкові поля по задачі
            #  передати списокм у змінну. Змінну вивести користувачу
            self._bot.send_message(chat_id,
                                   f"Process with task is: {task_description}")
