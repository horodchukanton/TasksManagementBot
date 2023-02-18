import logging
from typing import Union

import injector
from telebot.types import Message

from odoo_tasks_management.business_logic.procedures.authentication import (
    AuthenticationFactory,
)
from odoo_tasks_management.business_logic.base.exc import OperationAborted
from odoo_tasks_management.business_logic.base.operation import Operation
from odoo_tasks_management.messenger.telegram import Bot


class Router:
    # Contains information about current user position in the interface
    _running_operations = {}

    @injector.inject
    def __init__(
        self,
        authentication_factory: AuthenticationFactory,
    ):
        self._authentication_factory = authentication_factory

    def handle_message(
        self,
        bot: Bot,
        message: Message,
    ):
        # Log the received message
        logging.debug("Received message:\n %s", str(message))
        chat_id = message.chat.id

        # Handle a conversation
        if self._handle_existing_operation(bot, chat_id, message):
            return

        # Generic routes
        if message.text == "/start":  # TODO: also check if user is registered
            # Initialize the authentication process and store it as a running operation
            auth_logic = (
                self._authentication_factory.initialize_authentication()
            )
            self._running_operations[chat_id] = auth_logic.run(chat_id)
        else:
            # TODO: send the root menu keyboard
            # If the message is not recognized, send a message to the user
            bot.send_message(chat_id, "Message is not recognized")

    def _handle_existing_operation(
        self, bot: Bot, chat_id: Union[int, str], message: Message
    ) -> bool:
        # Check if there is an existing running operation for the user
        running_operation: Operation = self._running_operations.get(
            chat_id, None
        )
        if not running_operation:
            return False

        # If the running operation is finished, remove it
        if running_operation.is_finished:
            self._finish_operation(chat_id)
            return False

        try:
            # Handle the message using the running operation
            running_operation.on_next_message(chat_id, message)
            return True
        except OperationAborted:
            # If the operation is aborted, send a message to the user
            bot.send_message(chat_id, "Operation aborted")
            return True

    def _finish_operation(self, chat_id):
        # Remove the running operation for the user
        del self._running_operations[chat_id]
