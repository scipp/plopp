# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

from typing import Literal

import scipp as sc

from ..core import Node
from ..core.typing import FigureLike, Plottable
from ..graphics import Camera
from .common import _maybe_to_variable


def _preprocess_mesh(
    vertices: Plottable,
    faces: Plottable,
    facecolors: Plottable | None = None,
    vertexcolors: Plottable | None = None,
) -> sc.DataGroup:
    out = sc.DataGroup(
        {
            name: _maybe_to_variable(data)
            for name, data in zip(
                ['vertices', 'faces', 'facecolors', 'vertexcolors'],
                [vertices, faces, facecolors, vertexcolors],
            )
            if data is not None
        }
    )
    if out['vertices'].dtype != sc.DType.vector3:
        raise ValueError("Vertices must be of dtype vector3.")
    return out


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
    """
    Create a 3D mesh plot.

    .. versionadded:: 24.06.0

    Parameters
    ----------
    vertices:
        The vertices of the mesh. Must be a variable of dtype vector3.
    faces:
        The indices that construct the faces of the mesh.
    facecolors:
        The colors of the faces of the mesh.
    vertexcolors:
        The colors of the vertices of the mesh.
    figsize:
        The size of the figure.
    norm:
        The normalization of the colormap.
    title:
        The title of the figure.
    vmin:
        The minimum value of the colormap.
    vmax:
        The maximum value of the colormap.
    cmap:
        The colormap to use.
    camera:
        The camera configuration.
    """
    from ..graphics import mesh3dfigure

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
    return fig
