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
    *,
    vertices: Plottable,
    faces: Plottable,
    vertexcolors: Plottable | None = None,
    autoscale: bool = True,
    camera: Camera | None = None,
    cbar: bool = False,
    clabel: str | None = None,
    cmap: str = 'viridis',
    cmax: sc.Variable | float = None,
    cmin: sc.Variable | float = None,
    edgecolor: str | None = None,
    figsize: tuple[int, int] = (600, 400),
    logc: bool | None = None,
    nan_color: str | None = None,
    norm: Literal['linear', 'log', None] = None,
    title: str | None = None,
    vmax: sc.Variable | float = None,
    vmin: sc.Variable | float = None,
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
    autoscale:
        Automatically scale the colormap on updates if ``True``.
    camera:
        Initial camera configuration (position, target).
    cbar:
        Show colorbar if ``True``. If ``cbar`` is ``True``, the marker will be colored
        using the data values in the supplied data array.
    clabel:
        Label for colorscale (only applicable if ``cbar`` is ``True``).
    cmap:
        The colormap to be used for the colorscale (only applicable if ``cbar`` is
        ``True``).
    cmax:
        Upper limit for the colorscale (only applicable if ``cbar`` is ``True``).
    cmin:
        Lower limit for the colorscale (only applicable if ``cbar`` is ``True``).
    edgecolor:
        The color of the edges. If None, no edges are drawn.
    figsize:
        The size of the 3d rendering area, in pixels: ``(width, height)``.
    logc:
        Set to ``True`` for a logarithmic colorscale (only applicable if ``cbar`` is
        ``True``).
    nan_color:
        Color to use for NaN values in color mapping (only applicable if ``cbar`` is
        ``True``).
    norm:
        Set to ``'log'`` for a logarithmic colorscale (only applicable if ``cbar`` is
        ``True``). Legacy, prefer ``logc`` instead.
    title:
        The figure title.
    vmin:
        Lower bound for the colorscale for (only applicable if ``cbar`` is ``True``).
        Legacy, prefer ``cmin`` instead.
    vmax:
        Upper bound for the colorscale for (only applicable if ``cbar`` is ``True``).
        Legacy, prefer ``cmax`` instead.
    **kwargs:
        All other kwargs are forwarded the underlying plotting library.
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
        autoscale=autoscale,
        camera=camera,
        cbar=cbar,
        clabel=clabel,
        cmax=cmax,
        cmin=cmin,
        cmap=cmap,
        edgecolor=edgecolor,
        figsize=figsize,
        logc=logc,
        nan_color=nan_color,
        norm=norm,
        title=title,
        vmax=vmax,
        vmin=vmin,
        **kwargs,
    )
    return fig
