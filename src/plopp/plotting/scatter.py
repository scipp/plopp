# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import uuid
from functools import partial
from typing import Dict, Literal, Optional, Tuple, Union

import scipp as sc

from ..core.typing import PlottableMulti
from ..graphics import Camera
from .common import check_not_binned, from_compatible_lib, input_to_nodes


def _to_variable(var, coords):
    return coords[var] if isinstance(var, str) else var


def _preprocess_scatter(obj, x, y, name=None):
    da = from_compatible_lib(obj)
    check_not_binned(da)

    # if pos is not None:
    #     pos = _to_variable(pos, coords=da.coords)
    #     coords = {
    #         x: pos.fields.x,
    #         y: pos.fields.y,
    #     }
    # else:
    coords = {k: _to_variable(k, coords=da.coords) for k in (x, y)}
    out = sc.DataArray(data=da.data, masks=da.masks, coords=coords)
    if out.ndim != 1:
        out = out.flatten(to=uuid.uuid4().hex)
    out.name = name
    return out


def scatter(
    obj: PlottableMulti,
    *,
    x: str = 'x',
    y: str = 'y',
    color: Optional[
        Union[Dict[str, Union[str, sc.Variable]], Union[str, sc.Variable]]
    ] = None,
    size: Optional[
        Union[Dict[str, Union[str, sc.Variable]], Union[str, sc.Variable]]
    ] = None,
    figsize: Tuple[float, float] = None,
    norm: Literal['linear', 'log'] = 'linear',
    title: str = None,
    vmin: Union[sc.Variable, int, float] = None,
    vmax: Union[sc.Variable, int, float] = None,
    cmap: str = 'viridis',
    **kwargs,
):
    """Make a two-dimensional scatter plot."""
    from ..graphics import figure1d

    nodes = input_to_nodes(obj, processor=partial(_preprocess_scatter, x=x, y=y))

    return figure1d(
        *nodes,
        x=x,
        y=y,
        color=color,
        size=size,
        figsize=figsize,
        norm=norm,
        title=title,
        vmin=vmin,
        vmax=vmax,
        cmap=cmap,
        style='scatter',
        **kwargs,
    )
