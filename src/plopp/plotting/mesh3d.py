# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import uuid
from functools import partial
from typing import Dict, Literal, Optional, Tuple, Union

import scipp as sc

from ..core.typing import PlottableMulti
from ..graphics import Camera
from .common import check_not_binned, from_compatible_lib, input_to_nodes


def _to_variable(
    var: Union[str, sc.Variable], coords: Dict[str, sc.Variable]
) -> sc.Variable:
    return coords[var] if isinstance(var, str) else var


def _preprocess_mesh(
    obj: PlottableMulti,
    point: str,
    vertex: str,
    intensity: str | sc.Variable,
    mesh: sc.Variable,
    face: str,
    triangle: str,
    name: str | None = None,
) -> sc.DataArray:
    da = from_compatible_lib(obj)
    check_not_binned(da)

    if any(x not in da.data.dims for x in (point, vertex)):
        raise ValueError(f"Expected {point} and {vertex} but got {da.data.dims}")
    if isinstance(intensity, str):
        intensity_name = intensity
        intensity = da.coords[intensity_name]
    else:
        intensity_name = 'counts'
    if any(x not in (point, vertex) for x in intensity.dims):
        raise ValueError(f"Expected only {point} or {vertex} dims but got {intensity.dims}")

    coords = {intensity_name: intensity}
    out = sc.DataArray(data=da.data, masks=da.masks, coords=coords)
    if name is not None:
        out.name = name

    if any(x not in mesh.dims for x in (face, triangle)):
        raise ValueError(f"Expected {face} and {triangle} but got {mesh.dims}")

    return out


def mesh3d(
    obj: PlottableMulti,
    faces: sc.Variable,
    *,
    point: str = 'polyhedron',
    vertex: str = 'vertex',
    intensity: str = 'counts',
    face: str = 'face',
    triangle: str = 'triangle',
    figsize: Tuple[int, int] = (600, 400),
    norm: Literal['linear', 'log'] = 'linear',
    title: str = None,
    vmin: Union[sc.Variable, int, float] = None,
    vmax: Union[sc.Variable, int, float] = None,
    cmap: str = 'viridis',
    camera: Optional[Camera] = None,
    **kwargs,
):
    """Make a three-dimensional triangluated mesh plot.

    To specify the positions of the scatter points, you can use:

    - a single coordinate inside the supplied data array that has dtype ``vector3``
      (use the ``mesh`` parameter to specify the name of the coordinate).
    - three coordinates from the data array, whose names are specified using the
      ``x``, ``y``, and ``z`` arguments.

    Note that if ``mesh`` is used, ``x``, ``y``, and ``z`` must all be ``None``.

    Parameters
    ----------
    obj:
        The data array containing the data and the coordinates.
    faces:
        The triangulated face indexes for the data and coordinates
    point:
        The name of the polyhedron 'point' dimension in the data array data field
    vertex:
        The name of the vertex positions dimension for the data array data field
    intensity:
        The name of the intensity coordinate for the data array
    face:
        The name of the face dimension for the faces variable
    triangle:
        The name of the triangle dimension for the faces variable
    norm:
        Set to ``'log'`` for a logarithmic colorscale.
    figsize:
        The size of the 3d rendering area, in pixels: ``(width, height)``.
    title:
        The figure title.
    vmin:
        Lower bound for the colorscale.
    vmax:
        Upper bound for the colorscale.
    cmap:
        The name of the colormap.
    camera:
        Initial camera configuration (position, target).

    Returns
    -------
    :
        A three-dimensional interactive scatter plot.
    """
    from ..graphics import figure3d
    from ..widgets import Box, ToggleTool, TriCutTool

    if 'ax' in kwargs:
        raise ValueError(
            'Keyword "ax" detected. Embedding 3D scatter plots inside Matplotlib axes '
            'is not supported. See '
            'https://scipp.github.io/plopp/customization/subplots.html#FAQ:-subplots-with-3D-scatter-plots'  # noqa: E501
        )

    nodes = input_to_nodes(
        obj, processor=partial(_preprocess_mesh,
                               point=point, vertex=vertex, intensity=intensity,
                               mesh=faces, face=face, triangle=triangle)
    )

    fig = figure3d(
        *nodes,
        figsize=figsize,
        norm=norm,
        title=title,
        vmin=vmin,
        vmax=vmax,
        cmap=cmap,
        camera=camera,
        style='mesh',
        faces=faces,
        point=point,
        vertex=vertex,
        intensity=intensity,
        face=face,
        triangle=triangle,
        **kwargs,
    )
    tri_cutter = TriCutTool(fig)
    fig.toolbar['cut3d'] = ToggleTool(
        callback=tri_cutter.toggle_visibility,
        icon='cube',
        tooltip='Hide/show spatial cutting tool',
    )
    return Box([fig, tri_cutter])
