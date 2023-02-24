from typing import Dict, Union

from odoo_tasks_management.business_logic.base.operation import Operation
from odoo_tasks_management.messenger.telegram import Bot


class Procedure:

    _operation: Operation
    _context: Dict

    def __init__(self, bot: Bot):
        self._bot = bot
        self._context = {}

    def run(self, chat_id: Union[str, int]):
        self._operation.run(chat_id)
        return self._operation
