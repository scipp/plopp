# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from typing import Dict, List, Union

import scipp as sc
from numpy import ndarray
from scipp.typing import VariableLike

from ..core import input_node, widget_node
from ..graphics import figure1d, figure2d
from .common import preprocess, require_interactive_backend


class Slicer:
    """
    Class that slices out dimensions from the data and displays the resulting data as
    either a 1D line or a 2D image.

    Note:

    This class primarily exists to facilitate unit testing. When running unit tests, we
    are not in a Jupyter notebook, and the generated figures are not widgets that can
    be placed in the `Box` widget container at the end of the `slicer` function.
    We therefore place most of the code for creating a Slicer in this class, which is
    under unit test coverage. The thin `slicer` wrapper is not covered by unit tests.

    Parameters
    ----------
    obj:
        The input data.
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
                 obj: Union[VariableLike, ndarray, Dict[str, Union[VariableLike,
                                                                   ndarray]]],
                 keep: List[str] = None,
                 *,
                 crop: Dict[str, Dict[str, sc.Variable]] = None,
                 **kwargs):

        if isinstance(obj, (dict, sc.Dataset)):
            ds = sc.Dataset({
                key: preprocess(da, crop=crop, ignore_size=True)
                for key, da in obj.items()
            })
        else:
            da = preprocess(obj, crop=crop, ignore_size=True)
            ds = sc.Dataset({da.name: da})

        if keep is None:
            keep = ds.dims[-(2 if ds.ndim > 2 else 1):]

        if isinstance(keep, str):
            keep = [keep]

        if len(keep) == 0:
            raise ValueError(
                'Slicer plot: the list of dims to be kept cannot be empty.')
        if not all(dim in ds.dims for dim in keep):
            raise ValueError(
                f"Slicer plot: one or more of the requested dims to be kept {keep} "
                f"were not found in the input's dimensions {ds.dims}.")

        from ..widgets import SliceWidget, slice_dims

        self.data_nodes = [input_node(da) for da in ds.values()]

        self.slider = SliceWidget(
            sizes={dim: size
                   for dim, size in ds.sizes.items() if dim not in keep},
            coords=ds.meta)
        self.slider_node = widget_node(self.slider)
        self.slice_nodes = [
            slice_dims(data_node, self.slider_node) for data_node in self.data_nodes
        ]
        if len(keep) == 1:
            self.figure = figure1d(*self.slice_nodes, crop=crop, **kwargs)
        elif len(keep) == 2:
            self.figure = figure2d(*self.slice_nodes, crop=crop, **kwargs)


def slicer(obj: Union[VariableLike, ndarray, Dict[str, Union[VariableLike, ndarray]]],
           keep: List[str] = None,
           *,
           crop: Dict[str, Dict[str, sc.Variable]] = None,
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
    sl = Slicer(obj=obj, keep=keep, crop=crop, **kwargs)
    from ..widgets import Box
    return Box([sl.figure, sl.slider])
