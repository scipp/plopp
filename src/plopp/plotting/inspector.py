# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from typing import Literal

import scipp as sc

from ..core import Node
from ..core.typing import Plottable
from ..core.utils import coord_as_bin_edges
from ..graphics import imagefigure, linefigure
from .common import preprocess, require_interactive_figure


def _to_bin_edges(da: sc.DataArray, dim: str) -> sc.DataArray:
    """
    Convert dimension coords to bin edges.
    """
    for d in set(da.dims) - {dim}:
        da.coords[d] = coord_as_bin_edges(da, d)
    return da


def _apply_op(da: sc.DataArray, op: str, dim: str) -> sc.DataArray:
    out = getattr(sc, op)(da, dim=dim)
    if out.name:
        out.name = f'{op} of {out.name}'
    return out


def _slice_xy(da: sc.DataArray, xy: dict[str, dict[str, int]]) -> sc.DataArray:
    x = xy['x']
    y = xy['y']
    return da[y['dim'], y['value']][x['dim'], x['value']]


def inspector(
    obj: Plottable,
    dim: str | None = None,
    *,
    operation: Literal['sum', 'mean', 'min', 'max'] = 'sum',
    orientation: Literal['horizontal', 'vertical'] = 'horizontal',
    **kwargs,
):
    """
    Inspector takes in a three-dimensional input and applies a reduction operation
    (``'sum'`` by default) along one of the dimensions specified by ``dim``.
    It displays the result as a two-dimensional image.
    In addition, an 'inspection' tool is available in the toolbar which allows to place
    markers on the image which perform slicing at that position to retain only the third
    dimension and displays the resulting one-dimensional slice on the right hand side
    figure.

    Controls:
    - Click to make new point
    - Drag existing point to move it
    - Middle-click to delete point

    Parameters
    ----------
    obj:
        The object to be plotted.
    dim:
        The dimension along which to apply the reduction operation. This will also be
        the dimension that remains in the one-dimensional slices generated by adding
        markers on the image. If no dim is provided, the last (inner) dim of the input
        data will be used.
    operation:
        The operation to apply along the third (undisplayed) dimension specified by
        ``dim``.
    orientation:
        Display the two panels side-by-side ('horizontal') or one below the other
        ('vertical').
    **kwargs:
        See :py:func:`plopp.plot` for the full list of figure customization arguments.

    Returns
    -------
    :
        A :class:`Box` which will contain two :class:`Figure` and one slider widget.
    """

    f1d = linefigure()
    require_interactive_figure(f1d, 'inspector')

    in_node = Node(preprocess, obj, ignore_size=True)
    data = in_node()
    if data.ndim != 3:
        raise ValueError(
            'The inspector plot currently only works with '
            f'three-dimensional data, found {data.ndim} dims.'
        )
    if dim is None:
        dim = data.dims[-1]
    bin_edges_node = Node(_to_bin_edges, in_node, dim=dim)
    op_node = Node(_apply_op, da=bin_edges_node, op=operation, dim=dim)
    f2d = imagefigure(op_node, **kwargs)

    from ..widgets import Box, PointsTool

    pts = PointsTool(
        figure=f2d,
        input_node=bin_edges_node,
        func=_slice_xy,
        destination=f1d,
        tooltip="Activate inspector tool",
    )
    f2d.toolbar['inspect'] = pts
    out = [f2d, f1d]
    if orientation == 'horizontal':
        out = [out]
    return Box(out)
