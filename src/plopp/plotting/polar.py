# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from .plot import plot


def polar(*args, **kwargs):
    """
    Make a polar plot.

    See :func:`plot` for arguments.
    """

    return plot(*args, style='polar', **kwargs)
