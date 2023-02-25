from odoo_tasks_management.business_logic import router
from odoo_tasks_management.business_logic.base.operation import Operation, Prompt
from odoo_tasks_management.business_logic.base.procedure import Procedure
from odoo_tasks_management.messenger.telegram import Bot
from odoo_tasks_management.persistence.db import DB
from odoo_tasks_management.persistence.models import Task


class MarkTaskCompleted(Procedure):
    def __init__(self, db: DB, bot: Bot, task_title: str):
        super().__init__(bot)
        self._db = db
        self._router = router
        self._task_title = task_title
        self._operation = Operation(
            bot=bot,
            prompts=[
                Prompt(
                    buttons=["Спроба",
                             "Список задач проекту"],
                    expects=["text"],
                    handler=self.mark_task_completed,
                    text="Поки не впевнена",
                ),
            ],
            on_finish=lambda x: True,
        )

        self._context = {}

    def get_action(self, chat_id, message):
        action = message.text
        if action == "Відмітити задачу як виконану":
            self._bot.send_message(chat_id,
                f"Tasks status is Done: {self._task_title}")

    def mark_task_completed(self, chat_id, message):
        action = message.text
        if action == "Спроба":
            session = self._db.session()
            task = session.query(Task).filter_by(
                title=self._task_title
            ).one()
            task.status = 'Done'
            session.flush()
            session.commit()
            self._bot.send_message(chat_id,
                               f"Tasks status is Done: {self._task_title}")
