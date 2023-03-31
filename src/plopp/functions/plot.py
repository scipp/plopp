# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from typing import Dict, List, Literal, Optional, Tuple, Union

from numpy import ndarray
from scipp import Variable
from scipp.typing import VariableLike

from ..core import Node
from ..graphics import figure1d, figure2d
from .common import preprocess_multi


def plot(
    obj: Union[VariableLike, ndarray, Dict[str, Union[VariableLike, ndarray]]],
    *,
    aspect: Literal['auto', 'equal'] = 'auto',
    cbar: bool = True,
    coords: Optional[List[str]] = None,
    crop: Optional[Dict[str, Dict[str, Variable]]] = None,
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
    crop:
        Set the axis limits. Limits should be given as a dict with one entry per
        dimension to be cropped. Each entry should be a nested dict containing scalar
        values for ``'min'`` and/or ``'max'``. Example:
        ``da.plot(crop={'time': {'min': 2 * sc.Unit('s'), 'max': 40 * sc.Unit('s')}})``
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
        'crop': crop,
        'grid': grid,
        'norm': norm,
        'scale': scale,
        'title': title,
        'vmin': vmin,
        'vmax': vmax,
        'figsize': figsize,
        **kwargs,
    }

    data_arrays = preprocess_multi(
        obj, crop=crop, ignore_size=ignore_size, coords=coords
    )

    ndims = set()
    for da in data_arrays:
        ndims.add(da.ndim)
    if len(ndims) > 1:
        raise ValueError(
            'All items given to the plot function must have the same '
            f'number of dimensions. Found dimensions {ndims}.'
        )
    ndim = ndims.pop()
    if ndim == 1:
        return figure1d(
            *[Node(da) for da in data_arrays],
            errorbars=errorbars,
            mask_color=mask_color,
            **common_args,
        )
    elif ndim == 2:
        if len(data_arrays) > 1:
            raise ValueError(
                'The plot function can only plot a single 2d data entry. If you want '
                'to create multiple figures, see the documentation on subplots at '
                'https://scipp.github.io/plopp/customization/subplots.html. If you '
                'want to plot two images onto the same axes, use the lower-level '
                'plopp.figure2d function.'
            )
        return figure2d(
            *[Node(da) for da in data_arrays],
            aspect=aspect,
            cbar=cbar,
            **common_args,
        )
    else:
        raise ValueError(
            'The plot function can only plot 1d and 2d data, got input '
            f'with {ndim} dimensions'
        )
