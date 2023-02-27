import logging
from typing import Union

import injector
from telebot.types import Message

from odoo_tasks_management.business_logic.base.exc import OperationAborted
from odoo_tasks_management.business_logic.base.operation import Operation
from odoo_tasks_management.business_logic.base.procedure import Procedure
from odoo_tasks_management.business_logic.menu.projects_tasks_menu import ProjectsMenu
from odoo_tasks_management.business_logic.menu.create_task_menu import CreateTaskMenu
from odoo_tasks_management.business_logic.menu.root_menu import RootMenu
from odoo_tasks_management.business_logic.procedures.authentication import Authentication
from odoo_tasks_management.messenger.telegram import Bot
from odoo_tasks_management.odoo.client import OdooClient
from odoo_tasks_management.persistence.db import DB


class Router:
    # Contains information about current user position in the interface
    _running_operations = {}

    @injector.inject
    def __init__(
        self,
        db: DB,
        odoo_client: OdooClient
    ):
        self._db = db
        self._odoo_client = odoo_client

    def handle_message(
        self,
        bot: Bot,
        message: Message,
    ):
        # Log the received message
        logging.debug("Received message:\n %s", str(message))
        chat_id = message.chat.id

        if not self._check_user_authenticated(chat_id):
            authentication = self.get_authentication(bot)
            self._start_procedure(chat_id, authentication)

        # Handle a conversation
        if self._handle_existing_operation(bot, chat_id, message):
            return

        menu_logic = RootMenu(self, bot, self._db)
        self._start_procedure(chat_id, menu_logic)

    def _handle_existing_operation(
        self, bot: Bot, chat_id: Union[int, str], message: Message
    ) -> bool:
        # Check if there is an existing running operation for the user
        running_operation: Operation = self._running_operations.get(chat_id, None)
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
            return True

    def _finish_operation(self, chat_id):
        # Remove the running operation for the user
        del self._running_operations[chat_id]

    def _start_procedure(self, chat_id, procedure: Procedure):
        self._running_operations[chat_id] = procedure.run(chat_id)

    def proceed_with_procedure(self, chat_id, procedure: Procedure):
        self._finish_operation(chat_id)
        self._start_procedure(chat_id, procedure)

    def _check_user_authenticated(self, chat_id):
        return True

    def goto_authentication(self, chat_id, bot: Bot):
        self.proceed_with_procedure(
            chat_id,
            Authentication(bot=bot, db=self._db, odoo_client=self._odoo_client)
        )

    def goto_root_menu(self, chat_id, bot: Bot):
        self.proceed_with_procedure(
            chat_id,
            RootMenu(router=self, bot=bot, db=self._db)
        )

    def goto_projects_menu(self, chat_id, bot):
        self.proceed_with_procedure(
            chat_id,
            ProjectsMenu(router=self, db=self._db, bot=bot)
        )

    def goto_tasks_for_project_menu(self, chat_id, bot, project_name: str):
        self.proceed_with_procedure(
            chat_id,
            TasksForProjectMenu(db=self._db, router=self, bot=bot, project_name=project_name)
        )

    def goto_create_task_menu(self, chat_id, bot):
        self.proceed_with_procedure(
            chat_id,
            CreateTaskMenu(router=self, db=self._db, bot=bot)
        )

