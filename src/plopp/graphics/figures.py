# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from functools import partial

from ..backends import dispatcher
from ..core import Node
from ..core.typing import FigureLike
from .graphicalview import GraphicalView


def linefigure(*nodes: Node, **kwargs) -> FigureLike:
    view_maker = partial(
        GraphicalView,
        dims={'x': None},
        canvas_maker=dispatcher['2d']['canvas'],
        artist_maker=dispatcher['2d']['line'],
        colormapper=False,
    )
    return dispatcher['2d']['figure'](view_maker, *nodes, **kwargs)


def imagefigure(*nodes: Node, **kwargs) -> FigureLike:
    view_maker = partial(
        GraphicalView,
        dims={'y': None, 'x': None},
        canvas_maker=dispatcher['2d']['canvas'],
        artist_maker=dispatcher['2d']['image'],
        colormapper=True,
    )
    return dispatcher['2d']['figure'](view_maker, *nodes, **kwargs)


def scatterfigure(*nodes: Node, x: str, y: str, cbar: bool, **kwargs) -> FigureLike:
    view_maker = partial(
        GraphicalView,
        dims={'x': x, 'y': y},
        canvas_maker=dispatcher['2d']['canvas'],
        artist_maker=dispatcher['2d']['scatter'],
        colormapper=cbar,
    )
    if cbar:
        kwargs = {**kwargs, **{"edgecolors": "none"}}
    return dispatcher['2d']['figure'](view_maker, *nodes, x=x, y=y, cbar=cbar, **kwargs)


def scatter3dfigure(
    *nodes: Node, x: str, y: str, z: str, cbar: bool, **kwargs
) -> FigureLike:
    view_maker = partial(
        GraphicalView,
        dims={'x': x, 'y': y, 'z': z},
        canvas_maker=dispatcher['3d']['canvas'],
        artist_maker=dispatcher['3d']['scatter3d'],
        colormapper=cbar,
    )
    # if cbar:
    #     kwargs = {**kwargs, **{"edgecolors": "none"}}
    return dispatcher['3d']['figure'](
        view_maker, *nodes, x=x, y=y, z=z, cbar=cbar, **kwargs
    )
