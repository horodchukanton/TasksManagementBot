import threading

import injector

from odoo_tasks_management.business_logic.module import BusinessLogicModule
from odoo_tasks_management.business_logic.periodic.database_synchronization import (
    SynchronizeDatabase,
)
from odoo_tasks_management.business_logic.periodic.scheduler import Scheduler
from odoo_tasks_management.messenger.interface import Interface
from odoo_tasks_management.messenger.module import BotInterfaceModule
from odoo_tasks_management.odoo.module import OdooClientModule
from odoo_tasks_management.persistence.module import PersistenceModule
from odoo_tasks_management.settings import Settings


class MainModule(injector.Module):
    def configure(self, binder: injector.Binder):
        binder.install(PersistenceModule)
        # binder.install(WebApiModule)
        binder.install(OdooClientModule)
        binder.install(BotInterfaceModule)
        binder.install(BusinessLogicModule)

    @injector.provider
    @injector.singleton
    def _settings(self) -> Settings:
        return Settings()


def main():
    container = injector.Injector(MainModule())

    # Synchronize the database before running anything else
    sync = container.get(SynchronizeDatabase)
    sync.run()

    # Run bot
    bot = container.get(Interface)
    bot_thread = threading.Thread(target=bot.run)
    bot_thread.start()

    # Run periodic tasks scheduler
    periodic_tasks = container.get(Scheduler)
    scheduler_thread = threading.Thread(target=periodic_tasks.run)
    scheduler_thread.start()


if __name__ == "__main__":
    main()
