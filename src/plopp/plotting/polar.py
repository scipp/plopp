# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

# from functools import partial
# from typing import Dict, List, Literal, Optional, Tuple, Union

# from scipp import Variable

# from ..core.typing import PlottableMulti
# from ..graphics import figure1d, figure2d
from .plot import plot


def polar(*args, **kwargs):
    """
    Make a polar plot.

    See :func:`plot` for arguments.
    """

    return plot(*args, style='polar', **kwargs)
