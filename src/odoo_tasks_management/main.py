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
    # This class is a module that defines how to configure an injector.
    # It extends the 'injector.Module' class and overrides the 'configure' method
    # to specify the bindings to be installed in the injector.

    def configure(self, binder: injector.Binder):
        # This method configures the injector bindings.
        # It is called when the injector is being created.
        # The 'binder' parameter is an instance of the 'injector.Binder' class that is used to
        # define bindings.

        binder.install(PersistenceModule)
        # This line installs the bindings for the 'PersistenceModule' in the injector.
        # It will add the bindings defined in the 'PersistenceModule' to the bindings of the
        # 'MainModule'.
        # This is a way to organize the bindings of the injector into smaller, reusable modules.

        # binder.install(WebApiModule)
        # This line is commented out, but it would install the bindings for the 'WebApiModule' in
        # the injector.
        # It's likely that this module is not being used in the current codebase.

        binder.install(OdooClientModule)
        # This line installs the bindings for the 'OdooClientModule' in the injector.
        # It will add the bindings defined in the 'OdooClientModule' to the bindings of the
        # 'MainModule'.

        binder.install(BotInterfaceModule)
        # This line installs the bindings for the 'BotInterfaceModule' in the injector.
        # It will add the bindings defined in the 'BotInterfaceModule' to the bindings of the
        # 'MainModule'.

        binder.install(BusinessLogicModule)
        # This line installs the bindings for the 'BusinessLogicModule' in the injector.
        # It will add the bindings defined in the 'BusinessLogicModule' to the bindings of the
        # 'MainModule'.

    @injector.provider
    @injector.singleton
    def _settings(self) -> Settings:
        # This is a method that defines a binding for the 'Settings' class.
        # The 'injector.provider' decorator is used to specify that this method should be used to
        # create a new instance of 'Settings'.
        # The 'injector.singleton' decorator is used to specify that only one instance of
        # 'Settings' should be created and reused.
        # This means that every time an object in the injector needs an instance of 'Settings',
        # it will receive the same instance.

        return Settings()
        # This line creates a new instance of the 'Settings' class and returns it.


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
