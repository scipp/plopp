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


def deprecated_argument(old: str, new: str) -> None:
    warnings.warn(
        f'Argument "{old}" is deprecated and will be removed in a future release. '
        f'Please use "{new}" instead.',
        VisibleDeprecationWarning,
        stacklevel=2,
    )


def deprecated_attribute(old: str, new: str) -> None:
    warnings.warn(
        f'Attribute "{old}" is deprecated and will be removed in a future release. '
        f'Please use "{new}" instead.',
        VisibleDeprecationWarning,
        stacklevel=2,
    )


__all__ = ['deprecated', 'deprecated_argument', 'deprecated_attribute']
