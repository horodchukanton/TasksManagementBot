from business_logic.router import Router
from messenger.telegram import TelegramInterface
from odoo.client import OdooClient
from settings import Settings


class Main:

    def __init__(self, settings: Settings):
        self._settings: Settings = settings

        # self._odoo_client = OdooClient(settings.ODOO_URL, settings.ODOO_API_KEY)
        self._odoo_client = None
        self._router = Router(self._odoo_client)
        self._interface = TelegramInterface(settings, self._router)

    def run(self):
        self._interface.run()


if __name__ == '__main__':
    bot_settings = Settings()
    Main(bot_settings).run()
