import injector

from odoo_tasks_management.odoo.client import OdooClient
from odoo_tasks_management.settings import Settings


class OdooClientModule(injector.Module):

    @injector.provider
    def _odoo_client(self, settings: Settings) -> OdooClient:
        return OdooClient(settings)
