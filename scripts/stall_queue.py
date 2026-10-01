"""
Used by scripts/test_docker.sh to check that a stalled command queue makes
the health watchdog exit the process so Docker restarts the container.

Starts the real command queue and watchdog, then enqueues a command that
blocks forever, as a hung network call would.
"""

import threading

from src import health
from src.command.command import Command, Priority
from src.command.command_queue import command_queue
from src.logger import log


# pylint: disable=too-few-public-methods
class Stall(Command):
    """
    A command that never finishes.
    """

    def __init__(self) -> None:
        super().__init__("Stall", Priority.NORMAL)

    def execute(self) -> None:
        log.info("Stalling the command queue.")
        threading.Event().wait()


command_queue.start_in_background()
command_queue.enqueue(Stall())
health.start_health_watchdog()
threading.Event().wait()
