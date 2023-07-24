# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

# from typing import Literal

from .. import backends


def tiled(nrows: int, ncols: int, **kwargs):
    """ """
    return backends.tiled(nrows=nrows, ncols=ncols, **kwargs)
