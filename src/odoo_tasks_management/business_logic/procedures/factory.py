import injector

from odoo_tasks_management.business_logic.procedures.authentication import Authentication
from odoo_tasks_management.messenger.telegram import Bot
from odoo_tasks_management.odoo.client import OdooClient
from odoo_tasks_management.persistence.db import DB


class ProcedureFactory:
    @injector.inject
    def __init__(self, db: DB, bot: Bot, odoo_client: OdooClient):
        self._db = db
        self._bot = bot
        self._odoo_client = odoo_client

    def get_authentication(self):
        return Authentication(self._bot, self._db, self._odoo_client)
