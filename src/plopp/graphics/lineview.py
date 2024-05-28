# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from functools import partial

from .. import backends
from ..core.typing import FigureLike
from .graphicalview import GraphicalView


def linefigure(*nodes, **kwargs) -> FigureLike:
    """
    Create a figure to represent one-dimensional data from one or more graph node(s).

    .. versionadded:: 24.04.0

    Examples
    --------
    Create an input node and attach a ``linefigure`` as a view:

      >>> da = pp.data.data1d()
      >>> in_node = pp.Node(da)
      >>> fig = pp.linefigure(in_node)

    Visualize two data arrays on the same figure:

      >>> a = pp.data.data1d()
      >>> b = 3 * a
      >>> a_node = pp.Node(a)
      >>> b_node = pp.Node(b)
      >>> fig = pp.linefigure(a_node, b_node)

    With a customization argument to make the vertical scale logarithmic:

      >>> da = pp.data.data1d()
      >>> in_node = pp.Node(da)
      >>> fig = pp.linefigure(in_node, norm='log')
    """
    artist_args = {key: kwargs.pop(key) for key in ('errorbars', 'mask_color')}

    view_maker = partial(
        GraphicalView,
        dims={'x': None},
        canvas_maker=backends.canvas2d,
        artist_maker=partial(backends.line, **artist_args),
        colormapper=False,
    )
    return backends.figure2d(view_maker, *nodes, **kwargs)
