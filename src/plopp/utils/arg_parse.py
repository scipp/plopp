# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Scipp contributors (https://github.com/scipp)

from typing import Any


def parse_mutually_exclusive(**kwargs) -> Any | None:
    """
    Check that only one of the provided keyword arguments is not None.
    Return that one.
    """
    values = list(kwargs.values())
    if None not in values:
        raise ValueError(f'Only one of {list(kwargs.keys())} can be specified.')
    return ((set(values) - {None}) or {None}).pop()
