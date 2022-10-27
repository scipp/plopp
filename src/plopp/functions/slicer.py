# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .common import require_interactive_backend, preprocess
from .figure import figure1d, figure2d
from ..core import input_node, widget_node

from scipp import Variable, DataArray
from scipp.typing import VariableLike
from numpy import ndarray
from typing import Union, Dict, List


class Slicer:
    """
    Class that slices out dimensions from the data and displays the resulting data as
    either a 1D line or a 2D image.

    Parameters
    ----------
    da:
        The input data array.
    keep:
        The dimensions to be kept, all remaining dimensions will be sliced. This should
        be a list of dims. If no dims are provided, the last dim will be kept in the
        case of a 2-dimensional input, while the last two dims will be kept in the case
        of higher dimensional inputs.
    crop:
        Set the axis limits. Limits should be given as a dict with one entry per
        dimension to be cropped.
    **kwargs:
        The additional arguments are forwarded to the underlying 1D or 2D figures.
    """

    def __init__(self,
                 da: DataArray,
                 keep: List[str] = None,
                 *,
                 crop: Dict[str, Dict[str, Variable]] = None,
                 **kwargs):

        from ..widgets import SliceWidget, slice_dims

        self.data_node = input_node(da)

        if keep is None:
            keep = da.dims[-(2 if da.ndim > 2 else 1):]

        if isinstance(keep, str):
            keep = [keep]

        if len(keep) == 0:
            raise ValueError(
                'Slicer plot: the list of dims to be kept cannot be empty.')

        self.slider = SliceWidget(da, dims=list(set(da.dims) - set(keep)))
        self.slider_node = widget_node(self.slider)
        self.slice_node = slice_dims(self.data_node, self.slider_node)
        if len(keep) == 1:
            self.fig = figure1d(self.slice_node, crop=crop, **kwargs)
        elif len(keep) == 2:
            self.fig = figure2d(self.slice_node, crop=crop, **kwargs)


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
        values for ``'min'`` and/or ``'max'``. Example:
        ``da.plot(crop={'time': {'min': 2 * sc.Unit('s'), 'max': 40 * sc.Unit('s')}})``
    **kwargs:
        See :py:func:`plopp.plot` for the full list of figure customization arguments.

    Returns
    -------
    :
        A :class:`Box` which will contain a :class:`Figure` and slider widgets.
    """
    require_interactive_backend('slicer')
    da = preprocess(obj, crop=crop, ignore_size=True)
    from ..widgets import Box
    sl = Slicer(da=da, keep=keep, crop=crop, **kwargs)
    return Box([sl.fig, sl.slider])
