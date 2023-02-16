from typing import Callable, List, Union

from business_logic.base.exc import OperationAborted, PromptNotExpectedMessage
from messenger.telegram import Bot


class Prompt:
    def __init__(
        self,
        text: str,
        handler: Callable,
        expects: List[str],
    ):
        self._text = text
        self._expects = expects
        self._handler = handler

    def run(self, operation: 'Operation', chat_id):
        operation.bot.send_message(chat_id, self._text)

    def handle(self, chat_id, message):
        self._check_message_is_expected(message)
        self._handler(chat_id, message)

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
        on_finish: Callable
    ):
        self.bot = bot
        self._prompts = prompts
        self._on_finish = on_finish

    def run(self, chat_id: Union[int, str]):
        self._proceed(chat_id, 0)

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
        self._on_finish(chat_id)

    def _proceed(self, chat_id: Union[int, str], proceed_step: int):
        if self._current_prompt_num > len(self._prompts) - 1:
            return self.finish(chat_id)

        self._current_prompt = self._prompts[proceed_step]
        self._current_prompt.run(self, chat_id)
