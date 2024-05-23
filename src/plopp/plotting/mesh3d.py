# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import uuid
from functools import partial
from typing import Literal

import scipp as sc

from ..core.typing import FigureLike, PlottableMulti
from ..graphics import Camera
from .common import check_not_binned, from_compatible_lib, input_to_nodes


def _preprocess_mesh(
    obj: PlottableMulti,
    name: str | None = None,
) -> sc.DataArray:
    out = obj.copy(deep=False)
    if name is not None:
        out.name = name
    return out


def mesh3d(
    obj: PlottableMulti,
    *,
    vertices: str = 'vertices',
    faces: str = 'faces',
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

    nodes = input_to_nodes(obj, processor=_preprocess_mesh)

    fig = mesh3dfigure(
        *nodes,
        vertices=vertices,
        faces=faces,
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
