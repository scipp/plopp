# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

from ..core.typing import FigureLike, PlottableMulti
from .common import check_not_binned
from .plot import plot


def _convert_to_density(da: PlottableMulti, name: str = None):
    check_not_binned(da)
    widths = None
    for dim in da.dims:
        if not da.coords.is_edges(dim):
            raise ValueError(f"Coordinate {dim} must be bin edges for density_plot.")
        coord = da.coords[dim]
        w = coord[1:] - coord[:-1]
        if widths is None:
            widths = w
        else:
            widths = widths * w
    out = da / widths
    if name is not None:
        out.name = name
    return out


def density_plot(obj: PlottableMulti, **kwargs) -> FigureLike:
    """
    Make a histogram density plot, where the counts in each bin have been divided by
    the bin width (normalized).

    .. versionadded:: 24.05.0

    Parameters
    ----------
    obj:
        The object to be plotted. It must have a bin edge coordinate for each dimension.
    **kwargs:
        Additional keyword arguments passed to :func:`plopp.plot`.
    """
    return plot(obj, preprocessor=_convert_to_density, **kwargs)
