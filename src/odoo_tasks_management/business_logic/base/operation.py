from typing import Any, Callable, Dict, List, Optional, Union

from telebot import types
from telebot.types import CallbackQuery, Message
from telebot.util import quick_markup

from odoo_tasks_management.business_logic.base.exc import (
    OperationAborted,
    PromptNotExpectedMessage,
)
from odoo_tasks_management.messenger.telegram import Bot


class CallbackQueryAsMessage:
    def __init__(self, callback_query: CallbackQuery):
        self._callback_query = callback_query

    @property
    def text(self):
        return self._callback_query.data


class PromptMessage:

    def __init__(
        self,
        text: str,
        buttons: Union[List[str], Callable] = None,
        inline_buttons: Union[Dict[str, Dict[str, Any]], List[str], Callable] = None,
    ):
        self._text = text
        self._buttons = buttons
        self._inline_buttons = inline_buttons

    def build(self):
        message = {'text': self._text}

        if self._inline_buttons:
            message = {**message, 'reply_markup': self._build_inline_buttons()}
        elif self._buttons:
            message = {**message, 'reply_markup': self._build_buttons()}

        return message

    def _build_inline_buttons(self):
        if isinstance(self._inline_buttons, Callable):
            _inline_buttons = self._inline_buttons()
        elif isinstance(self._inline_buttons, List):
            _inline_buttons = {
                name: {'callback_data': name} for name in self._inline_buttons
            }
        else:
            # Assuming we got a dictionary with button names and callback data
            _inline_buttons = self._inline_buttons
        return quick_markup(_inline_buttons)

    def _build_buttons(self):
        items = []
        markup = types.ReplyKeyboardMarkup()
        for button in self._buttons:
            item = types.KeyboardButton(f'{button}')
            items.append(item)
        markup.row(*items)
        return markup


class Prompt:
    def __init__(
        self,
        handler: Callable,
        expects: List[str],
        message: Union[PromptMessage, Callable, str]
    ):
        self._expects = expects
        self._handler = handler
        self._message = message

    def run(self, operation: "Operation", chat_id):
        if message := self._build_message(operation, chat_id):
            operation.bot.send_message(chat_id, **message)
        return

    def _build_message(self, operation, chat_id: Union[str, int]):
        if isinstance(self._message, str):
            return {'text': self._message}
        if isinstance(self._message, Callable):
            return self._message(operation, chat_id)
        return self._message.build()

    def handle(self, chat_id, message: Union[Message, CallbackQuery]):
        if isinstance(message, Message):
            self._check_message_is_expected(message)
            self._handler(chat_id, message)
        else:
            self._handler(chat_id, CallbackQueryAsMessage(message))

    def _check_message_is_expected(self, message):
        if message.content_type not in self._expects:
            raise PromptNotExpectedMessage()


class Operation:
    is_finished = False

    _current_prompt = None
    _current_prompt_num = 0

    def __init__(
        self,
        bot: Bot,
        prompts: List[Prompt],
        on_finish: Optional[Callable] = None
    ):
        self.bot = bot
        self._prompts = prompts
        self._on_finish = on_finish

    def run(self, chat_id: Union[int, str]):
        return self._proceed(chat_id, 0)

    def on_next_message(self, chat_id: Union[int, str], message):
        try:
            self._current_prompt.handle(chat_id, message)
        except PromptNotExpectedMessage:
            self.abort(chat_id)

        self._current_prompt_num += 1
        return self._proceed(chat_id, self._current_prompt_num)

    def abort(self, chat_id, err_message: str = "Operation aborted"):
        self.bot.send_message(chat_id, err_message)
        self.is_finished = True
        raise OperationAborted()

    def finish(self, chat_id: Union[int, str]):
        self.is_finished = True
        if self._on_finish:
            self._on_finish(chat_id)

    def _proceed(self, chat_id: Union[int, str], proceed_step: int):
        if (
            self._current_prompt_num > len(self._prompts) - 1
            or self.is_finished
        ):
            return self.finish(chat_id)

        self._current_prompt = self._prompts[proceed_step]
        return self._current_prompt.run(self, chat_id)
