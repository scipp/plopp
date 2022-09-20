# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .common import is_interactive_backend, preprocess
from .figure import figure
from ..core import input_node, widget_node

from scipp import Variable
from scipp.typing import VariableLike
from numpy import ndarray
from typing import Union, Dict, List


def slicer(obj: Union[VariableLike, ndarray],
           keep: List[str] = None,
           *,
           crop: Dict[str, Dict[str, Variable]] = None,
           **kwargs):
    """
    Plot a multi-dimensional object by slicing one or more of the dimensions.
    This will produce one slider per sliced dimension, below the figure.

    Parameters
    ----------
    obj:
        The object to be plotted.
    keep:
        The dimensions to be kept, all remaining dimensions will be sliced. This should
        be a list of dims. If no dims are provided, the last dim will be kept in the
        case of a 2-dimensional input, while the last two dims will be kept in the case
        of higher dimensional inputs.
    crop:
        Set the axis limits. Limits should be given as a dict with one entry per
        dimension to be cropped. Each entry should be a nested dict containing scalar
        values for `'min'` and/or `'max'`. Example:
        `da.plot(crop={'time': {'min': 2 * sc.Unit('s'), 'max': 40 * sc.Unit('s')}})`
    **kwargs:
        See :py:func:`plopp.plot` for the full list of figure customization arguments.

    Returns
    -------
    :
        A :class:`Box` which will contain a :class:`Figure` and slider widgets.
    """
    if not is_interactive_backend():
        raise RuntimeError("The slicer can only be used with the interactive widget "
                           "backend. Use `%matplotlib widget` at the start of your "
                           "notebook.")
    from plopp.widgets import SliceWidget, slice_dims, Box
    da = preprocess(obj, crop=crop, ignore_size=True)
    a = input_node(da)

    if keep is None:
        keep = da.dims[-(2 if da.ndim > 2 else 1):]
    sl = SliceWidget(da, dims=list(set(da.dims) - set(keep)))
    w = widget_node(sl)
    slice_node = slice_dims(a, w)
    fig = figure(slice_node, **{**{'crop': crop}, **kwargs})
    return Box([fig, sl])
