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
    vertexcolors: Plottable | None = None,
) -> sc.DataArray:
    vertices, faces, vertexcolors = (
        _maybe_to_variable(data) if data is not None else None
        for data in (vertices, faces, vertexcolors)
    )

    if vertices.dtype != sc.DType.vector3:
        raise ValueError("Vertices must be of dtype vector3.")
    out = sc.DataArray(
        data=sc.broadcast(sc.empty(sizes={}), sizes=vertices.sizes),
        coords={
            'x': vertices.fields.x,
            'y': vertices.fields.y,
            'z': vertices.fields.z,
            'vertices': vertices,
            'faces': sc.scalar(faces),
        },
    )
    if vertexcolors is not None:
        out.data = vertexcolors
    return out


def mesh3d(
    vertices: Plottable,
    faces: Plottable,
    vertexcolors: Plottable | None = None,
    edgecolor: str | None = None,
    figsize: tuple[int, int] = (600, 400),
    logc: bool | None = None,
    title: str | None = None,
    cmin: sc.Variable | float = None,
    cmax: sc.Variable | float = None,
    cmap: str = 'viridis',
    camera: Camera | None = None,
    norm: Literal['linear', 'log'] = 'linear',
    vmin: sc.Variable | float = None,
    vmax: sc.Variable | float = None,
    **kwargs,
) -> FigureLike:
    """
    Create a 3D mesh plot.

    .. versionadded:: 24.09.2

    Parameters
    ----------
    vertices:
        The vertices of the mesh. Must be a variable of dtype vector3.
    faces:
        The indices that construct the faces of the mesh.
    vertexcolors:
        The colors of the vertices of the mesh. If ``None``, the mesh will have a
        single solid color.
    edgecolor:
        The color of the edges. If None, no edges are drawn.
    figsize:
        The size of the figure.
    logc:
        Set to ``True`` for a logarithmic colorscale.
    title:
        The title of the figure.
    cmin:
        Lower bound for the colorscale.
    cmax:
        Upper bound for the colorscale.
    cmap:
        The colormap to use.
    camera:
        The camera configuration.
    norm:
        The normalization of the colormap (legacy, prefer ``logc`` instead).
    vmin:
        The minimum value of the colormap (legacy, prefer ``cmin`` instead).
    vmax:
        The maximum value of the colormap (legacy, prefer ``cmax`` instead).
    **kwargs:
        Additional keyword arguments are passed to the underlying plotting library.
    """
    from ..graphics import mesh3dfigure

    input_node = Node(
        _preprocess_mesh,
        vertices=vertices,
        faces=faces,
        vertexcolors=vertexcolors,
    )

    fig = mesh3dfigure(
        input_node,
        vertexcolors=vertexcolors,
        edgecolor=edgecolor,
        figsize=figsize,
        logc=logc,
        title=title,
        cmin=cmin,
        cmax=cmax,
        cmap=cmap,
        camera=camera,
        norm=norm,
        vmin=vmin,
        vmax=vmax,
        **kwargs,
    )
    return fig
