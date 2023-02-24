from mockito import forget_invocations, mock, verify
from pytest import fixture
from telebot.types import Message

from odoo_tasks_management.business_logic.router import Router
from odoo_tasks_management.messenger.telegram import Bot
from odoo_tasks_management.odoo.client import OdooClient
from odoo_tasks_management.persistence.db import DB


class TestTasksMenu:

    @fixture
    def db(self):
        return mock(DB)

    @fixture
    def bot(self):
        return mock(Bot, strict=False)

    @fixture
    def odoo_client(self):
        return mock(OdooClient, strict=False)

    @fixture
    def router(self, db, odoo_client):
        return Router(db, odoo_client)

    @fixture
    def chat_id(self):
        return 123

    def test_close_task_invocation(self, router, chat_id, bot):
        def build_message(text):
            return mock(
                {
                    'chat': mock({'id': chat_id}),
                    'content_type': 'text',
                    'text': text
                },
                spec=Message
            )

        router.handle_message(bot, build_message('whatever'))
        verify(bot).send_message(chat_id, 'Привіт! Вітаю у Головному меню', ...)
        forget_invocations(bot)

        router.handle_message(bot, build_message('Мої Задачі'))
        verify(bot).send_message(chat_id, 'За яким проектом бажаєте переглянути задачі', ...)
        forget_invocations(bot)

        router.handle_message(bot, build_message("project1"))
        verify(bot).send_message(chat_id, 'Chosen project is: project1')
        verify(bot).send_message(chat_id, 'choose task', ...)
        forget_invocations(bot)

        router.handle_message(bot, build_message("task1"))
        verify(bot).send_message(chat_id, 'Chosen task is: task1')
        forget_invocations(bot)

        router.handle_message(bot, build_message("Відмітити задачу, як виконану"))
        verify(bot).send_message(chat_id, "Process with task is: Відмітити задачу, як виконану")
        verify(bot).send_message(
            chat_id,
            "назва задачі, опис задачі, виконавець, відповідальний, дедлайн, кількість годин",
            ...
        )
        forget_invocations(bot)

        router.handle_message(bot, build_message("Відмітити задачу як виконану"))
        verify(bot).send_message(chat_id, 'Tasks status is Done: task1')
        forget_invocations(bot)

        router.handle_message(bot, build_message('whatever'))
        verify(bot).send_message(chat_id, 'Привіт! Вітаю у Головному меню', ...)
        forget_invocations(bot)
