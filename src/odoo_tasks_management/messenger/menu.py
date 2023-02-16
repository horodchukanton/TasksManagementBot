from dataclasses import dataclass
from typing import Callable, List


@dataclass
class Button:
    title: str
    handler: Callable


class Menu:
    def __init__(self, buttons: List[Button]):
        self._buttons = buttons

    def to_message(self):
        # Convert list of buttons to telegram message
        pass
