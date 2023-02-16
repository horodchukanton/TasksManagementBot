import injector

from business_logic.module import BusinessLogicModule
from messenger.interface import Interface
from messenger.module import BotInterfaceModule
from odoo.module import OdooClientModule
from persistence.module import PersistenceModule
from settings import Settings


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


if __name__ == '__main__':
    container = injector.Injector(MainModule())
    app = container.get(Interface)
    app.run()
