import injector

from odoo_tasks_management.odoo.client import OdooClient
from .router import Router
from ..persistence.db import DB


class BusinessLogicModule(injector.Module):
    @injector.provider
    def _router(
        self, db: DB, odoo_client: OdooClient
    ) -> Router:
        return Router(db, odoo_client)
