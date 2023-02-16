from typing import Union


class Interface:

    def run(self):
        raise NotImplementedError()

    def send_message(self, chat_id: Union[int, str], message: str):
        raise NotImplementedError()
