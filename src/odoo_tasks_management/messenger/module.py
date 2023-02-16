import injector

from odoo_tasks_management.business_logic.router import Router
from odoo_tasks_management.messenger.interface import Interface
from odoo_tasks_management.messenger.telegram import Bot
from odoo_tasks_management.settings import Settings


class BotInterfaceModule(injector.Module):
    @injector.provider
    def _telegram_bot(self, settings: Settings) -> Bot:
        return Bot(settings)

    @injector.provider
    def _messenger_interface(self, bot: Bot, router: Router) -> Interface:
        return Interface(bot, router)
