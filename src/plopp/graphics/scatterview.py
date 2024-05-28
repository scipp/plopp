# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

from functools import partial

from .. import backends
from ..core.typing import FigureLike
from .graphicalview import GraphicalView


def scatterfigure(*nodes, **kwargs) -> FigureLike:
    """
    Create a figure to represent scatter data from one or more graph node(s).

    .. versionadded:: 24.04.0

    Examples
    --------
    Create an input node and attach a ``scatterfigure`` as a view:

      >>> da = pp.data.scatter()
      >>> in_node = pp.Node(da)
      >>> fig = pp.scatterfigure(in_node)

    A scatter figure with a color bar (using the data values for the color scale):

      >>> da = pp.data.scatter()
      >>> in_node = pp.Node(da)
      >>> fig = pp.scatterfigure(in_node, cbar=True)
    """
    artist_args = {key: kwargs.pop(key) for key in ('x', 'y', 'size', 'mask_color')}
    # Add cbar but we do not want to pop from kwargs
    artist_args['cbar'] = kwargs['cbar']

    view_maker = partial(
        GraphicalView,
        dims={'x': artist_args['x'], 'y': artist_args['y']},
        canvas_maker=backends.canvas2d,
        artist_maker=partial(backends.scatter, **artist_args),
        colormapper=kwargs['cbar'],
    )
    return backends.figure2d(view_maker, *nodes, **kwargs)
