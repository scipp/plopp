# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from typing import Dict, List, Literal, Optional, Tuple, Union

from numpy import ndarray
from scipp import Variable
from scipp.typing import VariableLike

from ..core import Node
from ..graphics import figure1d, figure2d
from .common import preprocess


def plot(
    *inputs: Union[
        VariableLike, ndarray, Dict[str, Union[VariableLike, ndarray]], Node
    ],
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
    inputs:
        The data objects to be plotted.
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

    # data_arrays = preprocess_multi(obj, ignore_size=ignore_size, coords=coords)
    flat_inputs = []
    for inp in inputs:
        if isinstance(inp, dict):
            flat_inputs.extend(inp.items())
        else:
            flat_inputs.append(('', inp))
    nodes = [
        Node(preprocess, inp, name=name, ignore_size=ignore_size, coords=coords)
        for name, inp in flat_inputs
    ]

    ndims = set()
    for n in nodes:
        ndims.add(n().ndim)
    # for da in data_arrays:
    #     ndims.add(da.ndim)
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
            raise ValueError(
                'The plot function can only plot a single 2d data entry. If you want '
                'to create multiple figures, see the documentation on subplots at '
                'https://scipp.github.io/plopp/customization/subplots.html. If you '
                'want to plot two images onto the same axes, use the lower-level '
                'plopp.figure2d function.'
            )
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
