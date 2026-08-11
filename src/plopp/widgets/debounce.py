# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

import asyncio
from collections.abc import Callable
from functools import wraps


def debounce(fn: Callable, *, wait: float):
    """
    Wrap a function so that its execution is postponed until `wait` seconds have
    elapsed since the last time it was invoked.

    If there is no running event loop, the function is called immediately. This is
    useful in synchronous contexts such as tests and scripts, where delayed execution
    cannot be scheduled without blocking or using another thread.
    """
    handle: asyncio.TimerHandle | None = None

    @wraps(fn)
    def debounced(*args, **kwargs):
        nonlocal handle

        def call_it():
            nonlocal handle
            handle = None
            fn(*args, **kwargs)

        if handle is not None:
            handle.cancel()
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            call_it()
        else:
            handle = loop.call_later(wait, call_it)

    return debounced
