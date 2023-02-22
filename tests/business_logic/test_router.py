from mockito import ANY, mock, verify, when
from pytest import fixture, mark

from odoo_tasks_management.business_logic.procedures.authentication import (
    Authentication,
)
from odoo_tasks_management.business_logic.procedures.factory import ProcedureFactory
from odoo_tasks_management.business_logic.router import Router
from odoo_tasks_management.messenger.telegram import Bot


class TestRouter:
    @fixture
    def authentication(self, message_chat_id):
        auth = mock(Authentication)
        when(auth).run(message_chat_id).thenReturn(mock({"is_finished": True}))
        return auth

    @fixture
    def authentication_factory(self, authentication):
        factory = mock(ProcedureFactory)
        when(factory).get_authentication().thenReturn(authentication)
        return factory

    @fixture
    def router(self, authentication_factory):
        return Router(authentication_factory)

    @fixture
    def bot(self):
        bot = mock(Bot)
        when(bot).send_message(ANY, ANY).thenReturn()
        return bot

    @fixture
    def message_text(self):
        return None

    @fixture
    def message_chat_id(self):
        return 123

    @fixture
    def message(self, message_text, message_chat_id):
        return mock(
            {"text": message_text, "chat": mock({"id": message_chat_id})}
        )

    @mark.parametrize("message_text", ["/start"])
    def test_calls_authentication_on_start_command(
        self, router, bot, authentication, message
    ):
        router.handle_message(bot, message)

        # Checking that authentication was started
        verify(authentication).run(message.chat.id)

    @mark.parametrize("message_text", ["whatever non specified message"])
    def test_yield_on_unknown_message(self, router, bot, message):
        router.handle_message(bot, message)

        # Checking that bot responded to unknown message
        verify(bot).send_message(message.chat.id, "Message is not recognized")
