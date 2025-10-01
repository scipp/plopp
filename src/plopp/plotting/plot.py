# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from functools import partial

from scipp import Variable

from ..core.typing import FigureLike, PlottableMulti
from ..graphics import imagefigure, linefigure
from .common import input_to_nodes, preprocess, raise_multiple_inputs_for_2d_plot_error
from .signature import with_plotting_params


@with_plotting_params()
def plot(
    obj: PlottableMulti,
    *,
    cbar: bool = True,
    coords: list[str] | None = None,
    errorbars: bool = True,
    ignore_size: bool = False,
    mask_color: str = 'black',
    nan_color: str | None = None,
    legend: bool | tuple[float, float] = True,
    cmin: Variable | float | None = None,
    cmax: Variable | float | None = None,
    logc: bool | None = None,
    clabel: str | None = None,
    **kwargs,
) -> FigureLike:
    """Plot a Scipp object.

    Parameters
    ----------
    obj:
        The object to be plotted.
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

    # common_args = {
    #     'aspect': aspect,
    #     'grid': grid,
    #     'norm': norm,
    #     'scale': scale,
    #     'title': title,
    #     'vmin': vmin,
    #     'vmax': vmax,
    #     'figsize': figsize,
    #     'xlabel': xlabel,
    #     'ylabel': ylabel,
    #     'xmin': xmin,
    #     'xmax': xmax,
    #     'ymin': ymin,
    #     'ymax': ymax,
    #     'logx': logx,
    #     'logy': logy,
    #     **kwargs,
    # }

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
            **kwargs,
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
            **kwargs,
        )
    else:
        raise ValueError(
            'The plot function can only plot 1d and 2d data, got input '
            f'with {ndim} dimensions'
        )
