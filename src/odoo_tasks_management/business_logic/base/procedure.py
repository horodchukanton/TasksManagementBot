from typing import Union

from odoo_tasks_management.business_logic.base.operation import Operation
from odoo_tasks_management.messenger.telegram import Bot


class Procedure:

    _operation: Operation

    def __init__(self, bot: Bot):
        self._bot = bot

    def run(self, chat_id: Union[str, int]):
        self._operation.run(chat_id)
        return self._operation
