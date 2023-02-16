import injector

from odoo_tasks_management.business_logic.procedures.authenticaton import (
    AuthenticationFactory,
)
from odoo_tasks_management.messenger.telegram import Bot
from odoo_tasks_management.odoo.client import OdooClient


class BusinessLogicModule(injector.Module):
    @injector.provider
    def _authentication_factory(
        self, odoo_client: OdooClient, bot: Bot
    ) -> AuthenticationFactory:
        return AuthenticationFactory(odoo_client, bot)
