# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from functools import partial

from .. import backends
from ..core.typing import FigureLike
from .graphicalview import GraphicalView


def imagefigure(*nodes, **kwargs) -> FigureLike:
    """
    Create a figure to represent two-dimensional data from one or more graph node(s).

    .. versionadded:: 24.04.0

    Examples
    --------
    Create an input node and attach an ``imagefigure`` as a view:

      >>> da = pp.data.data2d()
      >>> in_node = pp.Node(da)
      >>> fig = pp.imagefigure(in_node)

    With a customization argument to make the color scale logarithmic:

      >>> da = pp.data.data2d()
      >>> in_node = pp.Node(da)
      >>> fig = pp.imagefigure(in_node, norm='log')
    """

    view_maker = partial(
        GraphicalView,
        dims={'y': None, 'x': None},
        canvas_maker=backends.canvas2d,
        artist_maker=backends.image,
        colormapper=True,
    )
    return backends.figure2d(view_maker, *nodes, **kwargs)
