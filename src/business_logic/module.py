import injector

from business_logic.authenticaton import AuthenticationFactory
from messenger.telegram import Bot
from odoo.client import OdooClient


class BusinessLogicModule(injector.Module):

    @injector.provider
    def _authentication_factory(
        self, odoo_client: OdooClient, bot: Bot
    ) -> AuthenticationFactory:
        return AuthenticationFactory(odoo_client, bot)
