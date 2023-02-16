import injector

from odoo_tasks_management.persistence.db import DB
from odoo_tasks_management.settings import Settings


class PersistenceModule(injector.Module):
    @injector.provider
    def _db(self, settings: Settings) -> DB:
        return DB(settings)
