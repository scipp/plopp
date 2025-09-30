# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Scipp contributors (https://github.com/scipp)

from typing import Any


def parse_mutually_exclusive(**kwargs) -> Any | None:
    """
    Check that only one of the provided keyword arguments is not None.
    Return that one.
    Additionally, if the final value is a string (either 'linear' or 'log'), return a
    boolean indicating whether the value is 'log'.
    """
    values = list(kwargs.values())
    if None not in values:
        raise ValueError(f'Only one of {list(kwargs.keys())} can be specified.')
    out = ([v for v in values if v is not None] or [None])[0]
    match out:
        case 'linear':
            return False
        case 'log':
            return True
        case _:
            return out
