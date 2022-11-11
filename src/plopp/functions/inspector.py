# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .plot import plot
from .common import require_interactive_backend, preprocess
from .figure import figure1d, figure2d
from ..core import input_node, node, Node, View
from ..core.utils import coord_as_bin_edges

import scipp as sc
from numpy import ndarray
from typing import Any, Union, Dict, Optional, Literal


def inspector(obj: Union[ndarray, sc.Variable, sc.DataArray],
              dim: Optional[str] = None,
              *,
              operation: Literal['sum', 'mean', 'min', 'max'] = 'sum',
              orientation: Literal['horizontal', 'vertical'] = 'horizontal',
              **kwargs):
    """
    Inspector takes in a three-dimensional input and applies a reduction operation
    (``sum`` by default) along one of the dimensions specified by ``dim``.
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

    if obj.ndim != 3:
        raise ValueError('The inspector plot currently only works with '
                         f'three-dimensional data, found {obj.ndim} dims.')
    require_interactive_backend('inspector')

    from ..widgets import InspectTool

    da = preprocess(obj, crop=crop, ignore_size=True)
    if dim is None:
        dim = da.dims[-1]
    # Convert dimension coords to bin edges (safe to change coords in-place because
    # the output of `preprocess` is already a copy).
    for d in set(da.dims) - {dim}:
        da.coords[d] = coord_as_bin_edges(da, d)

    a = input_node(da)
    p = plot(getattr(sc, operation)(da, dim=dim))
    fig1d = figure1d()
    p.add_tool(InspectTool, root_node=a, fig1d=fig1d)

    from ..widgets import Box
    out = [p, fig1d]
    if orientation == 'horizontal':
        out = [out]
    return Box(out)
