import injector

from business_logic.router import Router
from messenger.interface import Interface
from messenger.telegram import Bot
from settings import Settings


class BotInterfaceModule(injector.Module):

    @injector.provider
    def _telegram_bot(self, settings: Settings) -> Bot:
        return Bot(settings)

    @injector.provider
    def _messenger_interface(self, bot: Bot, router: Router) -> Interface:
        return Interface(bot, router)
