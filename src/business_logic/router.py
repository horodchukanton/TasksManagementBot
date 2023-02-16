from business_logic.authenticaton import Authentication
from business_logic.base.exc import OperationAborted
from business_logic.base.operation import Operation
from messenger.base import Interface
from odoo.client import OdooClient


class Router:

    # Contains information about a session for user
    _running_operations = {}

    def __init__(self, odoo_client: OdooClient):
        self._odoo_client = odoo_client

    def handle_message(self, bot: Interface, message):
        chat_id = message.chat.id

        # Handle a conversation
        running_operation: Operation = self._running_operations.get(chat_id, None)
        if running_operation:
            if running_operation.is_finished:
                del self._running_operations[chat_id]
            else:
                try:
                    return running_operation.on_next_message(chat_id, message)
                except OperationAborted:
                    bot.send_message(chat_id, "Operation aborted")
                    del self._running_operations[chat_id]
                    return

        # Generic routes
        if message.text == '/start':
            operation = Authentication(self._odoo_client, bot)
            self._running_operations[chat_id] = operation.run(chat_id)
        else:
            bot.send_message(chat_id, "Message is not recognized")
