# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

import asyncio
from collections.abc import Callable


class Timer:
    """
    From:
    https://ipywidgets.readthedocs.io/en/8.0.2/examples/Widget%20Events.html#Debouncing
    """

    def __init__(self, timeout: float, callback: Callable):
        self._timeout = timeout
        self._callback = callback

    async def _job(self):
        await asyncio.sleep(self._timeout)
        self._callback()

    def start(self):
        self._task = asyncio.ensure_future(self._job())

    def cancel(self):
        self._task.cancel()


def debounce(wait: float):
    """
    Decorator that will postpone a function's
    execution until after `wait` seconds
    have elapsed since the last time it was invoked.

    From:
    https://ipywidgets.readthedocs.io/en/8.0.2/examples/Widget%20Events.html#Debouncing
    """

    def decorator(fn: Callable):
        timer = None

        def debounced(*args, **kwargs):
            nonlocal timer

            def call_it():
                fn(*args, **kwargs)

            if timer is not None:
                timer.cancel()
            timer = Timer(wait, call_it)
            timer.start()

        return debounced

    return decorator
