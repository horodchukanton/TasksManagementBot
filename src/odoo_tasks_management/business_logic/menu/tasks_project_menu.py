from telebot.types import Message
from typing import Union

from odoo_tasks_management.business_logic.base.operation import Operation, Prompt
from odoo_tasks_management.business_logic.base.procedure import Procedure
from odoo_tasks_management.business_logic.menu.mark_task_completed import \
    MarkTaskCompleted
from odoo_tasks_management.messenger.telegram import Bot
from odoo_tasks_management.persistence.db import DB


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
                        "Ознайомитись із описом",
                        "Відмітити задачу, як виконану"]
                ),
            ],
            on_finish=lambda x: True
        )

        self._context = {}

    def _get_tasks(self, project_name):
        if project_name == "project1":
            return ["task1", "task2", "task3", "task4"]
        elif project_name == "project2":
            return ["task5", "task6", "task7", "task8"]
        elif project_name == "project3":
            return ["task9", "task10", "task11", "task12"]
        elif project_name == "project4":
            btns = []
            for i in range(10):
                btns.append("Одн велика і довга назва задачі")
            return btns

    def task_chosen(self, chat_id, message):
        chosen_task = message.text
        self._bot.send_message(chat_id, f"Chosen task is: {chosen_task}")
        self._context['task'] = chosen_task

    def chosen_process_with_tasks(self, chat_id: Union[int, str], message):
        if message.text == "Відмітити задачу, як виконану":
            mark_task = message.text
            self._bot.send_message(chat_id, f"Process with task is: {mark_task}")

            mark_tasks_as_done = MarkTaskCompleted(
                self._db, self._bot, self._context['task']
            )
            self._router.proceed_with_procedure(
                chat_id,
                mark_tasks_as_done
            )
        elif message.text == "Ознайомитись із описом":
            task_description = message.text
            # TODO: по ID витягнути з БД опис обов'язкові поля по задачі
            #  передати списокм у змінну. Змінну вивести користувачу
            self._bot.send_message(chat_id,
                                   f"Process with task is: {task_description}")






