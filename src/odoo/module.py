import injector

from odoo.client import OdooClient
from settings import Settings


class OdooClientModule(injector.Module):

    @injector.provider
    def _odoo_client(self, settings: Settings) -> OdooClient:
        return OdooClient(settings.ODOO_URL, settings.ODOO_API_KEY)
