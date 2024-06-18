# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from collections.abc import Callable
from functools import partial

from .. import dispatcher
from ..core import Node
from ..core.typing import FigureLike
from .graphicalview import GraphicalView


def linefigure(*nodes: Node, **kwargs) -> FigureLike:
    view_maker = partial(
        GraphicalView,
        dims={'x': None},
        canvas_maker=dispatcher['canvas'],
        artist_maker=dispatcher['line'],
        colormapper=False,
    )
    return dispatcher['figure'](view_maker, *nodes, **kwargs)


def imagefigure(*nodes: Node, **kwargs) -> FigureLike:
    view_maker = partial(
        GraphicalView,
        dims={'y': None, 'x': None},
        canvas_maker=dispatcher['canvas'],
        artist_maker=dispatcher['image'],
        colormapper=True,
    )
    return dispatcher['figure'](view_maker, *nodes, **kwargs)


def scatterfigure(*nodes: Node, x: str, y: str, cbar: bool, **kwargs) -> FigureLike:
    view_maker = partial(
        GraphicalView,
        dims={'x': x, 'y': y},
        canvas_maker=dispatcher['canvas'],
        artist_maker=dispatcher['scatter'],
        colormapper=cbar,
    )
    if cbar:
        kwargs = {**kwargs, **{"edgecolors": "none"}}
    return dispatcher['figure'](view_maker, *nodes, x=x, y=y, cbar=cbar, **kwargs)
