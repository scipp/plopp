# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

import functools
import warnings
from collections.abc import Callable

from .core.typing import VisibleDeprecationWarning


def deprecated(message: str = '') -> Callable:
    def decorator(function: Callable) -> Callable:
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f'{function.__name__} is deprecated. {message}',
                VisibleDeprecationWarning,
                stacklevel=2,
            )
            return function(*args, **kwargs)

        return wrapper

    return decorator


__all__ = ['deprecated']
