# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import uuid
from functools import partial
from typing import Literal

import scipp as sc

from ..core.typing import FigureLike, PlottableMulti
from ..graphics import Camera
from .common import check_not_binned, from_compatible_lib, input_to_nodes


def _preprocess_scatter(
    obj: PlottableMulti,
    x: str,
    y: str,
    z: str,
    pos: str | None,
    name: str | None = None,
) -> sc.DataArray:
    da = from_compatible_lib(obj)
    check_not_binned(da)

    if pos is not None:
        coords = {k: getattr(da.coords[pos].fields, k) for k in (x, y, z)}
    else:
        coords = {k: da.coords[k] for k in (x, y, z)}

    out = sc.DataArray(data=da.data, masks=da.masks, coords=coords)
    if out.ndim != 1:
        out = out.flatten(to=uuid.uuid4().hex)
    if name is not None:
        out.name = name
    return out


def scatter3d(
    obj: PlottableMulti,
    *,
    x: str = 'x',
    y: str = 'y',
    z: str = 'z',
    pos: str | None = None,
    figsize: tuple[int, int] = (600, 400),
    norm: Literal['linear', 'log'] = 'linear',
    title: str | None = None,
    vmin: sc.Variable | float = None,
    vmax: sc.Variable | float = None,
    cbar: bool = False,
    cmap: str = 'viridis',
    camera: Camera | None = None,
    **kwargs,
) -> FigureLike:
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
    from ..graphics import scatter3dfigure
    from ..widgets import ClippingPlanes, ToggleTool

    if 'ax' in kwargs:
        raise ValueError(
            'Keyword "ax" detected. Embedding 3D scatter plots inside Matplotlib axes '
            'is not supported. See '
            'https://scipp.github.io/plopp/customization/subplots.html#FAQ:-subplots-with-3D-scatter-plots'
        )

    nodes = input_to_nodes(
        obj, processor=partial(_preprocess_scatter, x=x, y=y, z=z, pos=pos)
    )

    fig = scatter3dfigure(
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
        cbar=cbar,
        camera=camera,
        **kwargs,
    )
    clip_planes = ClippingPlanes(fig)
    fig.toolbar['cut3d'] = ToggleTool(
        callback=clip_planes.toggle_visibility,
        icon='layer-group',
        tooltip='Hide/show spatial cutting tool',
    )
    fig.bottom_bar.add(clip_planes)
    return fig
