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
    autoscale: bool = True,
    camera: Camera | None = None,
    cbar: bool = False,
    clabel: str | None = None,
    cmap: str = 'viridis',
    cmax: sc.Variable | float = None,
    cmin: sc.Variable | float = None,
    figsize: tuple[int, int] = (600, 400),
    logc: bool | None = None,
    nan_color: str | None = None,
    norm: Literal['linear', 'log'] | None = None,
    title: str | None = None,
    vmax: sc.Variable | float = None,
    vmin: sc.Variable | float = None,
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
        Lower limit for the colorscale for (only applicable if ``cbar`` is ``True``).
        Legacy, prefer ``cmin`` instead.
    vmax:
        Upper limit for the colorscale for (only applicable if ``cbar`` is ``True``).
        Legacy, prefer ``cmax`` instead.
    **kwargs:
        All other kwargs are forwarded the underlying plotting library.

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
        autoscale=autoscale,
        camera=camera,
        cbar=cbar,
        clabel=clabel,
        cmax=cmax,
        cmin=cmin,
        cmap=cmap,
        figsize=figsize,
        logc=logc,
        nan_color=nan_color,
        norm=norm,
        title=title,
        vmax=vmax,
        vmin=vmin,
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
