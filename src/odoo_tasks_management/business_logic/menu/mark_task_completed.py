from typing import Union

from odoo_tasks_management.business_logic import router
from odoo_tasks_management.business_logic.base.operation import Operation, Prompt
from odoo_tasks_management.business_logic.base.procedure import Procedure
from odoo_tasks_management.messenger.telegram import Bot
from odoo_tasks_management.persistence.db import DB


class MarkTaskCompleted(Procedure):
    def __init__(self, db: DB, bot: Bot, chosen_task: str):
        super().__init__(bot)
        self._db = db
        self._router = router
        self._chosen_task = chosen_task
        self._operation = Operation(
            bot=bot,
            prompts=[
                Prompt(
                    buttons=["Відмітити задачу як виконану",
                             "Повернутись до списку задач проекту"],
                    expects=["text"],
                    handler=self.get_action,
                    text="назва задачі, опис задачі, виконавець, відповідальний, дедлайн, кількість годин",
                ),
            ],
            on_finish=lambda x: True,
        )

        self._context = {}

    def get_action(self, chat_id, message):
        action = message.text
        if action == "Відмітити задачу як виконану":
            self._bot.send_message(chat_id,
                f"Tasks status is Done: {self._chosen_task}")
        # elif action == "Повернутись до списку задач проекту":
        #     self.start_tasks_for_project_menu
        #     )




