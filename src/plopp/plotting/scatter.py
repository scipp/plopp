# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import uuid
from functools import partial
from typing import Literal, Optional, Tuple, Union

import scipp as sc

from ..core.typing import PlottableMulti
from .common import check_not_binned, from_compatible_lib, input_to_nodes


def _preprocess_scatter(
    obj: PlottableMulti,
    x: str,
    y: str,
    size: Optional[str],
    name: Optional[str] = None,
):
    da = from_compatible_lib(obj)
    check_not_binned(da)

    cnames = [x, y]
    if size is not None:
        cnames.append(size)
    coords = {k: da.coords[k] for k in cnames}
    out = sc.DataArray(data=da.data, masks=da.masks, coords=coords)
    if out.ndim != 1:
        out = out.flatten(to=uuid.uuid4().hex)
    if name is not None:
        out.name = name
    return out


def scatter(
    obj: PlottableMulti,
    *,
    x: str = 'x',
    y: str = 'y',
    size: Optional[str] = None,
    figsize: Tuple[float, float] = None,
    norm: Literal['linear', 'log'] = 'linear',
    title: str = None,
    vmin: Union[sc.Variable, int, float] = None,
    vmax: Union[sc.Variable, int, float] = None,
    cbar: bool = False,
    cmap: str = 'viridis',
    **kwargs,
):
    """Make a two-dimensional scatter plot."""
    from ..graphics import scatterfigure

    nodes = input_to_nodes(
        obj, processor=partial(_preprocess_scatter, x=x, y=y, size=size)
    )

    return scatterfigure(
        *nodes,
        x=x,
        y=y,
        size=size,
        figsize=figsize,
        norm=norm,
        title=title,
        vmin=vmin,
        vmax=vmax,
        cmap=cmap,
        cbar=cbar,
        **kwargs,
    )
