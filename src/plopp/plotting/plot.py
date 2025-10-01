# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from functools import partial

from scipp import Variable

from ..core.typing import FigureLike, PlottableMulti
from ..graphics import imagefigure, linefigure
from .common import input_to_nodes, preprocess, raise_multiple_inputs_for_2d_plot_error
from .signature import with_2d_plot_params


@with_2d_plot_params()
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

    Returns
    -------
    :
        A figure.
    """

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
