import injector

from odoo_tasks_management.messenger.telegram import Bot
from odoo_tasks_management.odoo.client import OdooClient
from .procedures.factory import ProcedureFactory
from ..persistence.db import DB


class BusinessLogicModule(injector.Module):
    @injector.provider
    def _operation_factory(
        self, db: DB, bot: Bot, odoo_client: OdooClient
    ) -> ProcedureFactory:
        return ProcedureFactory(db, bot, odoo_client)
