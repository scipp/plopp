# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from functools import partial
from typing import Literal

from scipp import Variable

from ..core.typing import FigureLike, PlottableMulti
from ..graphics import imagefigure, linefigure
from .common import input_to_nodes, preprocess, raise_multiple_inputs_for_2d_plot_error


def plot(
    obj: PlottableMulti,
    *,
    aspect: Literal['auto', 'equal', None] = None,
    cbar: bool = True,
    coords: list[str] | None = None,
    errorbars: bool = True,
    figsize: tuple[float, float] | None = None,
    grid: bool = False,
    ignore_size: bool = False,
    mask_color: str = 'black',
    nan_color: str | None = None,
    norm: Literal['linear', 'log', None] = None,
    scale: dict[str, str] | None = None,
    title: str | None = None,
    vmin: Variable | float | None = None,
    vmax: Variable | float | None = None,
    legend: bool | tuple[float, float] = True,
    xmin: Variable | float | None = None,
    xmax: Variable | float | None = None,
    ymin: Variable | float | None = None,
    ymax: Variable | float | None = None,
    cmin: Variable | float | None = None,
    cmax: Variable | float | None = None,
    logx: bool = False,
    logy: bool = False,
    logc: bool = False,
    xlabel: str | None = None,
    ylabel: str | None = None,
    clabel: str | None = None,
    **kwargs,
) -> FigureLike:
    """Plot a Scipp object.

    Parameters
    ----------
    obj:
        The object to be plotted.
    aspect:
        Aspect ratio for the axes.
    cbar:
        Show colorbar in 2d plots if ``True``.
    coords:
        If supplied, use these coords instead of the input's dimension coordinates.
    errorbars:
        Show errorbars in 1d plots if ``True``.
    figsize:
        The width and height of the figure, in inches.
    grid:
        Show grid if ``True``.
    ignore_size:
        If ``True``, skip the check that prevents the rendering of very large data
        objects.
    mask_color:
        Color of masks in 1d plots.
    nan_color:
        Color to use for NaN values in 2d plots.
    norm:
        Set to ``'log'`` for a logarithmic y-axis (1d plots) or logarithmic colorscale
        (2d plots).
    scale:
        Change axis scaling between ``log`` and ``linear``. For example, specify
        ``scale={'tof': 'log'}`` if you want log-scale for the ``tof`` dimension.
    title:
        The figure title.
    vmin:
        Lower bound for data to be displayed (y-axis for 1d plots, colorscale for
        2d plots).
    vmax:
        Upper bound for data to be displayed (y-axis for 1d plots, colorscale for
        2d plots).
    legend:
        Show legend if ``True``. If ``legend`` is a tuple, it should contain the
        ``(x, y)`` coordinates of the legend's anchor point in axes coordinates.
    xmin:
        Lower limit for x-axis.
    xmax:
        Upper limit for x-axis.
    ymin:
        Lower limit for y-axis.
    ymax:
        Upper limit for y-axis.
    cmin:
        Lower limit for colorscale (2d plots only).
    cmax:
        Upper limit for colorscale (2d plots only).
    logx:
        If ``True``, use logarithmic scale for x-axis.
    logy:
        If ``True``, use logarithmic scale for y-axis.
    logc:
        If ``True``, use logarithmic scale for colorscale (2d plots only).
    xlabel:
        Label for x-axis.
    ylabel:
        Label for y-axis.
    clabel:
        Label for colorscale (2d plots only).
    **kwargs:
        All other kwargs are directly forwarded to Matplotlib, the underlying plotting
        library. The underlying functions called are the following:

        - 1d data with a non bin-edge coordinate: ``plot``
        - 1d data with a bin-edge coordinate: ``step``
        - 2d data: ``pcolormesh``

    Returns
    -------
    :
        A figure.
    """

    common_args = {
        'aspect': aspect,
        'grid': grid,
        'norm': norm,
        'scale': scale,
        'title': title,
        'vmin': vmin,
        'vmax': vmax,
        'figsize': figsize,
        'xlabel': xlabel,
        'ylabel': ylabel,
        'xmin': xmin,
        'xmax': xmax,
        'ymin': ymin,
        'ymax': ymax,
        'logx': logx,
        'logy': logy,
        **kwargs,
    }

    nodes = input_to_nodes(
        obj, processor=partial(preprocess, ignore_size=ignore_size, coords=coords)
    )

    ndims = set()
    for n in nodes:
        ndims.add(n().ndim)
    if len(ndims) > 1:
        raise ValueError(
            'All items given to the plot function must have the same '
            f'number of dimensions. Found dimensions {ndims}.'
        )
    ndim = ndims.pop()
    if ndim == 1:
        return linefigure(
            *nodes,
            errorbars=errorbars,
            mask_color=mask_color,
            legend=legend,
            **common_args,
        )
    elif ndim == 2:
        if len(nodes) > 1:
            raise_multiple_inputs_for_2d_plot_error(origin='plot')
        return imagefigure(
            *nodes,
            cbar=cbar,
            cmin=cmin,
            cmax=cmax,
            clabel=clabel,
            logc=logc,
            nan_color=nan_color,
            **common_args,
        )
    else:
        raise ValueError(
            'The plot function can only plot 1d and 2d data, got input '
            f'with {ndim} dimensions'
        )
