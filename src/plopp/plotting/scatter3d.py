# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import uuid
from functools import partial
from typing import Literal, Optional, Tuple, Union

import scipp as sc

from ..core.typing import PlottableMulti
from ..graphics import Camera
from .common import check_not_binned, from_compatible_lib, input_to_nodes


def _to_variable(var, coords):
    return coords[var] if isinstance(var, str) else var


def _preprocess_scatter(obj, x, y, z, pos, name=None):
    da = from_compatible_lib(obj)
    check_not_binned(da)

    if pos is not None:
        pos = _to_variable(pos, coords=da.coords)
        coords = {
            x: pos.fields.x,
            y: pos.fields.y,
            z: pos.fields.z,
        }
    else:
        coords = {k: _to_variable(k, coords=da.coords) for k in (x, y, z)}

    out = sc.DataArray(data=da.data, masks=da.masks, coords=coords)
    if out.ndim != 1:
        out = out.flatten(to=uuid.uuid4().hex)
    out.name = name
    return out


def scatter3d(
    obj: PlottableMulti,
    *,
    x: str = 'x',
    y: str = 'y',
    z: str = 'z',
    pos: str = None,
    figsize: Tuple[int, int] = (600, 400),
    norm: Literal['linear', 'log'] = 'linear',
    title: str = None,
    vmin: Union[sc.Variable, int, float] = None,
    vmax: Union[sc.Variable, int, float] = None,
    cmap: str = 'viridis',
    camera: Optional[Camera] = None,
    **kwargs,
):
    """Make a three-dimensional scatter plot.

    To specify the positions of the scatter points, you can use:

    - a single coordinate inside the supplied data array that has dtype ``vector3``
      (use the ``pos`` parameter to specify the name of the coordinate).
    - three coordinates from the data array, whose names are specified using the
      ``x``, ``y``, and ``z`` arguments.

    Note that if ``pos`` is used, ``x``, ``y``, and ``z`` must all be ``None``.

    Parameters
    ----------
    obj:
        The data array containing the data and the coordinates.
    x:
        The name of the coordinate that is to be used for the X positions.
    y:
        The name of the coordinate that is to be used for the Y positions.
    z:
        The name of the coordinate that is to be used for the Z positions.
    pos:
        The name of the vector coordinate that is to be used for the positions.
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
        obj, processor=partial(_preprocess_scatter, x=x, y=y, z=z, pos=pos)
    )

    fig = figure3d(
        *nodes,
        x=x,
        y=y,
        z=z,
        figsize=figsize,
        norm=norm,
        title=title,
        vmin=vmin,
        vmax=vmax,
        cmap=cmap,
        camera=camera,
        **kwargs,
    )
    tri_cutter = TriCutTool(fig)
    fig.toolbar['cut3d'] = ToggleTool(
        callback=tri_cutter.toggle_visibility,
        icon='cube',
        tooltip='Hide/show spatial cutting tool',
    )
    return Box([fig, tri_cutter])
