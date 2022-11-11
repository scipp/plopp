# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .plot import plot
from .common import require_interactive_backend
from .figure import figure1d, figure2d

import scipp as sc
from numpy import ndarray
from typing import Any, Union, Dict, Literal


def linecutter(obj: Union[ndarray, sc.Variable, sc.DataArray],
               *,
               orientation: Literal['horizontal', 'vertical'] = 'horizontal',
               **kwargs):
    """
    Linecutter takes in a two-dimensional input.
    It provides a tool for drawing lines on the image which display a cut (or profile)
    of the data in the second panel.

    Controls:
    - Click to make a new line
    - Click and drag on an existing vertex to move it
    - Right-click to drag an entire line
    - Middle-click to delete a line

    Parameters
    ----------
    obj:
        The object to be plotted.
    orientation:
        Display the two panels side-by-side ('horizontal') or one below the other
        ('vertical').
    **kwargs:
        See :py:func:`plopp.plot` for the full list of figure customization arguments.

    Returns
    -------
    :
        A :class:`Box` which will contain a two-dimensional figure to display the
        original data, and a one-dimensional figure to display the cuts.
    """

    if obj.ndim != 2:
        raise ValueError('The linecutter plot currently only works with '
                         f'two-dimensional data, found {obj.ndim} dims.')
    require_interactive_backend('linecutter')

    from ..widgets import LineCutTool
    p = plot(obj, **kwargs)
    fig1d = figure1d(ls='solid', marker=None)
    p.add_tool(LineCutTool, fig1d=fig1d)

    from ..widgets import Box
    out = [p, fig1d]
    if orientation == 'horizontal':
        out = [out]
    return Box(out)
