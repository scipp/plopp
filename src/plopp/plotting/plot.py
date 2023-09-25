# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from functools import partial
from typing import Dict, List, Literal, Optional, Tuple, Union

from scipp import Variable

from ..core.typing import PlottableMulti
from ..graphics import figure1d, figure2d
from .common import input_to_nodes, preprocess, raise_multiple_inputs_for_2d_plot_error


def plot(
    obj: PlottableMulti,
    *,
    aspect: Literal['auto', 'equal'] = 'auto',
    cbar: bool = True,
    coords: Optional[List[str]] = None,
    errorbars: bool = True,
    figsize: Tuple[float, float] = None,
    grid: bool = False,
    ignore_size: bool = False,
    mask_color: str = 'black',
    norm: Literal['linear', 'log'] = 'linear',
    scale: Optional[Dict[str, str]] = None,
    title: Optional[str] = None,
    vmin: Optional[Union[Variable, int, float]] = None,
    vmax: Optional[Union[Variable, int, float]] = None,
    autoscale: Literal['auto', 'grow'] = 'auto',
    legend: Union[bool, Tuple[float, float]] = True,
    **kwargs,
):
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
    autoscale:
        The behavior of the axis (1d plots) or the color range limits (2d plots).
        If ``auto``, the limits automatically adjusts every time the data changes.
        If ``grow``, the limits are allowed to grow with time but they do not shrink.
    legend:
        Show legend if ``True``. If ``legend`` is a tuple, it should contain the
        ``(x, y)`` coordinates of the legend's anchor point in axes coordinates.
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
        'grid': grid,
        'norm': norm,
        'scale': scale,
        'title': title,
        'vmin': vmin,
        'vmax': vmax,
        'autoscale': autoscale,
        'figsize': figsize,
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
        return figure1d(
            *nodes,
            errorbars=errorbars,
            mask_color=mask_color,
            legend=legend,
            **common_args,
        )
    elif ndim == 2:
        if len(nodes) > 1:
            raise_multiple_inputs_for_2d_plot_error(origin='plot')
        return figure2d(
            *nodes,
            aspect=aspect,
            cbar=cbar,
            **common_args,
        )
    else:
        raise ValueError(
            'The plot function can only plot 1d and 2d data, got input '
            f'with {ndim} dimensions'
        )
