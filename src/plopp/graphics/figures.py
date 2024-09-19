# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from functools import partial

import scipp as sc

from .. import backends
from ..core import Node
from ..core.typing import FigureLike
from .graphicalview import GraphicalView


def linefigure(
    *nodes: Node,
    vmin: sc.Variable | float | None = None,
    vmax: sc.Variable | float | None = None,
    **kwargs,
) -> FigureLike:
    view_maker = partial(
        GraphicalView,
        dims={'x': None},
        canvas_maker=partial(
            backends.get(group='2d', name='canvas'),
            user_vmin=vmin,
            user_vmax=vmax,
        ),
        artist_maker=backends.get(group='2d', name='line'),
        colormapper=False,
    )
    return backends.get(group='2d', name='figure')(view_maker, *nodes, **kwargs)


def imagefigure(*nodes: Node, **kwargs) -> FigureLike:
    view_maker = partial(
        GraphicalView,
        dims={'y': None, 'x': None},
        canvas_maker=backends.get(group='2d', name='canvas'),
        artist_maker=backends.get(group='2d', name='image'),
        colormapper=True,
    )
    return backends.get(group='2d', name='figure')(view_maker, *nodes, **kwargs)


def scatterfigure(
    *nodes: Node, x: str = 'x', y: str = 'y', cbar: bool = False, **kwargs
) -> FigureLike:
    view_maker = partial(
        GraphicalView,
        dims={'x': x, 'y': y},
        canvas_maker=backends.get(group='2d', name='canvas'),
        artist_maker=backends.get(group='2d', name='scatter'),
        colormapper=cbar,
    )
    if cbar:
        kwargs = {**kwargs, **{"edgecolors": "none"}}
    return backends.get(group='2d', name='figure')(
        view_maker, *nodes, x=x, y=y, cbar=cbar, **kwargs
    )


def scatter3dfigure(
    *nodes: Node, x: str = 'x', y: str = 'y', z: str = 'z', cbar: bool = False, **kwargs
) -> FigureLike:
    view_maker = partial(
        GraphicalView,
        dims={'x': x, 'y': y, 'z': z},
        canvas_maker=backends.get(group='3d', name='canvas'),
        artist_maker=backends.get(group='3d', name='scatter3d'),
        colormapper=cbar,
    )
    return backends.get(group='3d', name='figure')(
        view_maker, *nodes, x=x, y=y, z=z, cbar=cbar, **kwargs
    )


def mesh3dfigure(*nodes: Node, vertexcolors, **kwargs) -> FigureLike:
    colormapper = vertexcolors is not None
    view_maker = partial(
        GraphicalView,
        dims={'x': 'x', 'y': 'y', 'z': 'z'},
        canvas_maker=backends.get(group='3d', name='canvas'),
        artist_maker=backends.get(group='3d', name='mesh3d'),
        colormapper=colormapper,
    )
    return backends.get(group='3d', name='figure')(
        view_maker, *nodes, cbar=colormapper, **kwargs
    )
