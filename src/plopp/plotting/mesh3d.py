# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import uuid
from functools import partial
from typing import Literal

import scipp as sc

from ..core import Node
from ..core.typing import FigureLike, Plottable, PlottableMulti
from ..graphics import Camera
from .common import _maybe_to_variable, input_to_nodes


def _preprocess_mesh(
    vertices: Plottable,
    faces: Plottable,
    facecolors: Plottable | None = None,
    vertexcolors: Plottable | None = None,
) -> sc.DataGroup:
    return sc.DataGroup(
        {
            name: _maybe_to_variable(data)
            for name, data in zip(
                ['vertices', 'faces', 'facecolors', 'vertexcolors'],
                [vertices, faces, facecolors, vertexcolors],
            )
            if data is not None
        }
    )


def mesh3d(
    vertices: Plottable,
    faces: Plottable,
    facecolors: Plottable | None = None,
    vertexcolors: Plottable | None = None,
    figsize: tuple[int, int] = (600, 400),
    norm: Literal['linear', 'log'] = 'linear',
    title: str | None = None,
    vmin: sc.Variable | float = None,
    vmax: sc.Variable | float = None,
    cmap: str = 'viridis',
    camera: Camera | None = None,
    **kwargs,
) -> FigureLike:
    """ """
    from ..graphics import mesh3dfigure
    # from ..widgets import ClippingPlanes, ToggleTool

    input_node = Node(
        _preprocess_mesh,
        vertices=vertices,
        faces=faces,
        facecolors=facecolors,
        vertexcolors=vertexcolors,
    )

    fig = mesh3dfigure(
        input_node,
        figsize=figsize,
        norm=norm,
        title=title,
        vmin=vmin,
        vmax=vmax,
        cmap=cmap,
        camera=camera,
        **kwargs,
    )
    # clip_planes = ClippingPlanes(fig)
    # fig.toolbar['cut3d'] = ToggleTool(
    #     callback=clip_planes.toggle_visibility,
    #     icon='layer-group',
    #     tooltip='Hide/show spatial cutting tool',
    # )
    # fig.bottom_bar.add(clip_planes)
    return fig
