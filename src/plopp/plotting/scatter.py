# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

import uuid
from functools import partial

import scipp as sc

from ..core.typing import FigureLike, PlottableMulti
from .common import check_not_binned, from_compatible_lib, input_to_nodes
from .signature import with_plotting_params


def _preprocess_scatter(
    obj: PlottableMulti,
    x: str,
    y: str,
    size: str | None,
    name: str | None = None,
):
    da = from_compatible_lib(obj)
    check_not_binned(da)

    cnames = [x, y]
    if isinstance(size, str):
        cnames.append(size)
    coords = {k: da.coords[k] for k in cnames}
    out = sc.DataArray(data=da.data, masks=da.masks, coords=coords)
    if out.ndim != 1:
        out = out.flatten(to=uuid.uuid4().hex)
    if name is not None:
        out.name = name
    return out


@with_plotting_params()
def scatter(
    obj: PlottableMulti,
    *,
    x: str = 'x',
    y: str = 'y',
    size: str | float | None = None,
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
    size:
        The size of the marker. If a float is supplied, all markers will have the same
        size. If a string is supplied, it will be the name of the coordinate that is to
        be used for the size of the markers.
    **kwargs:
        All other kwargs are forwarded the underlying plotting library.
    """
    from ..graphics import scatterfigure

    nodes = input_to_nodes(
        obj, processor=partial(_preprocess_scatter, x=x, y=y, size=size)
    )

    return scatterfigure(*nodes, x=x, y=y, size=size, **kwargs)
