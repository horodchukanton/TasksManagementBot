import injector

from odoo_tasks_management.messenger.telegram import Bot
from odoo_tasks_management.odoo.client import OdooClient
from .procedures.authentication import (
    AuthenticationFactory,
)
from ..persistence.db import DB


class BusinessLogicModule(injector.Module):
    @injector.provider
    def _authentication_factory(
        self, db: DB, bot: Bot, odoo_client: OdooClient
    ) -> AuthenticationFactory:
        return AuthenticationFactory(db, bot, odoo_client)
