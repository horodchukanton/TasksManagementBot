from dataclasses import dataclass
from threading import Timer
from typing import Callable

import injector

from odoo_tasks_management.settings import Settings
from .check_for_notification import CheckForNotificationsPeriodic
from .database_synchronization import SynchronizeDatabase


@dataclass
class PeriodicTask:
    handler: Callable
    interval: int


class RepeatTimer(Timer):
    def run(self):
        # pylint: disable=too-many-function-args
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


class Scheduler:
    @injector.inject
    def __init__(
        self,
        settings: Settings,
        db_sync: SynchronizeDatabase,
        deadline_notifications: CheckForNotificationsPeriodic,
    ):
        self._settings = settings
        self._periodics = [
            PeriodicTask(
                handler=db_sync.run,
                interval=settings.SCHEDULE_DB_SYNC * 60,
            ),
            PeriodicTask(
                handler=deadline_notifications.run,
                interval=settings.SCHEDULE_DEADLINE_NOTIFICATIONS * 60,
            ),
        ]

    def run(self):
        for periodic in self._periodics:
            timer = RepeatTimer(periodic.interval, periodic.handler)
            timer.start()
