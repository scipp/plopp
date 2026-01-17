# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

import uuid
from functools import partial
from typing import Literal

import scipp as sc

from ..core.typing import FigureLike, PlottableMulti
from .common import check_not_binned, check_size, from_compatible_lib, input_to_nodes


def _preprocess_scatter(
    obj: PlottableMulti,
    x: str,
    y: str,
    pos: str | None,
    size: str | None,
    name: str | None = None,
    ignore_size: bool = False,
):
    da = from_compatible_lib(obj)
    check_not_binned(da)

    if pos is not None:
        coords = {k: getattr(da.coords[pos].fields, k) for k in (x, y)}
    else:
        coords = {k: da.coords[k] for k in (x, y)}

    if isinstance(size, str):
        coords[size] = da.coords[size]
    out = sc.DataArray(data=da.data, masks=da.masks, coords=coords)
    if out.ndim != 1:
        out = out.flatten(to=uuid.uuid4().hex)
    if not ignore_size:
        check_size(out)
    if name is not None:
        out.name = name
    return out


def scatter(
    obj: PlottableMulti,
    *,
    x: str = 'x',
    y: str = 'y',
    pos: str | None = None,
    aspect: Literal['auto', 'equal', None] = None,
    autoscale: bool = True,
    cbar: bool = False,
    clabel: str | None = None,
    cmap: str = 'viridis',
    cmax: sc.Variable | float | None = None,
    cmin: sc.Variable | float | None = None,
    figsize: tuple[float, float] | None = None,
    grid: bool = False,
    ignore_size: bool = False,
    legend: bool | tuple[float, float] = True,
    logc: bool | None = None,
    logx: bool | None = None,
    logy: bool | None = None,
    mask_color: str = 'black',
    nan_color: str | None = None,
    norm: Literal['linear', 'log', None] = None,
    scale: dict[str, str] | None = None,
    size: str | float | None = None,
    title: str | None = None,
    vmax: sc.Variable | float | None = None,
    vmin: sc.Variable | float | None = None,
    xlabel: str | None = None,
    xmax: sc.Variable | float | None = None,
    xmin: sc.Variable | float | None = None,
    ylabel: str | None = None,
    ymax: sc.Variable | float | None = None,
    ymin: sc.Variable | float | None = None,
    **kwargs,
) -> FigureLike:
    """
    Make a two-dimensional scatter plot.

    .. versionadded:: 24.04.0

    Parameters
    ----------
    obj:
        The object to be plotted.
    x:
        The name of the coordinate that is to be used for the X positions.
    y:
        The name of the coordinate that is to be used for the Y positions.
    pos:
        The name of the vector coordinate that is to be used for the positions.
    aspect:
        Aspect ratio for the axes.
    autoscale:
        Automatically scale the axes/colormap if ``True``.
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
        The width and height of the figure, in inches.
    grid:
        Show grid if ``True``.
    ignore_size:
        If ``True``, skip the check that prevents the rendering of very large data.
    legend:
        Show legend if ``True``. If ``legend`` is a tuple, it should contain the
        ``(x, y)`` coordinates of the legend's anchor point in axes coordinates.
    logc:
        Set to ``True`` for a logarithmic colorscale (only applicable if ``cbar`` is
        ``True``).
    logx:
        If ``True``, use logarithmic scale for x-axis.
    logy:
        If ``True``, use logarithmic scale for y-axis.
    mask_color:
        Color of markers for masked data.
    nan_color:
        Color to use for NaN values in color mapping (only applicable if ``cbar`` is
        ``True``).
    norm:
        Set to ``'log'`` for a logarithmic colorscale (only applicable if ``cbar`` is
        ``True``). Legacy, prefer ``logc`` instead.
    scale:
        Change axis scaling between ``log`` and ``linear``. For example, specify
        ``scale={'time': 'log'}`` if you want log-scale for the ``time`` dimension.
        Legacy, prefer ``logx`` and ``logy`` instead.
    title:
        The figure title.
    vmin:
        Lower limit for the colorscale for (only applicable if ``cbar`` is ``True``).
        Legacy, prefer ``cmin`` instead.
    vmax:
        Upper limit for the colorscale for (only applicable if ``cbar`` is ``True``).
        Legacy, prefer ``cmax`` instead.
    xlabel:
        Label for x-axis.
    xmax:
        Upper limit for x-axis.
    xmin:
        Lower limit for x-axis.
    ylabel:
        Label for y-axis.
    ymax:
        Upper limit for y-axis.
    ymin:
        Lower limit for y-axis.
    **kwargs:
        All other kwargs are forwarded the underlying plotting library.
    """
    from ..graphics import scatterfigure

    nodes = input_to_nodes(
        obj,
        processor=partial(
            _preprocess_scatter, x=x, y=y, pos=pos, size=size, ignore_size=ignore_size
        ),
    )

    return scatterfigure(
        *nodes,
        aspect=aspect,
        autoscale=autoscale,
        cbar=cbar,
        clabel=clabel,
        cmap=cmap,
        cmax=cmax,
        cmin=cmin,
        figsize=figsize,
        grid=grid,
        legend=legend,
        logc=logc,
        logx=logx,
        logy=logy,
        mask_color=mask_color,
        nan_color=nan_color,
        norm=norm,
        scale=scale,
        size=size,
        title=title,
        vmax=vmax,
        vmin=vmin,
        x=x,
        xlabel=xlabel,
        xmax=xmax,
        xmin=xmin,
        y=y,
        ylabel=ylabel,
        ymax=ymax,
        ymin=ymin,
        **kwargs,
    )
