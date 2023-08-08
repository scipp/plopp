# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import warnings
from functools import reduce
from typing import Dict, List, Literal, Union

import scipp as sc
from numpy import ndarray
from scipp.typing import VariableLike

from ..core import Node, widget_node
from ..graphics import figure1d, figure2d
from .common import preprocess_multi, require_interactive_backend


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
    autoscale:
        The behavior of the y-axis (1d plots) and color range (2d plots) limits.
        If ``auto``, the limits automatically adjusts every time the data changes.
        If ``grow``, the limits are allowed to grow with time but they do not shrink.
        If ``fixed``, the limits are fixed to the full data range and do not change
        with time.
    vmin:
        The minimum value of the y-axis (1d plots) or color range (2d plots).
    vmax:
        The maximum value of the y-axis (1d plots) or color range (2d plots).
    **kwargs:
        The additional arguments are forwarded to the underlying 1D or 2D figures.
    """

    def __init__(
        self,
        obj: Union[VariableLike, ndarray, Dict[str, Union[VariableLike, ndarray]]],
        keep: List[str] = None,
        *,
        autoscale: Literal['auto', 'grow', 'fixed'] = 'auto',
        vmin: Union[VariableLike, int, float] = None,
        vmax: Union[VariableLike, int, float] = None,
        **kwargs,
    ):
        data_arrays = preprocess_multi(obj, ignore_size=True)
        ds = sc.Dataset({da.name: da for da in data_arrays})

        if keep is None:
            keep = ds.dims[-(2 if ds.ndim > 2 else 1) :]

        if isinstance(keep, str):
            keep = [keep]

        if len(keep) == 0:
            raise ValueError(
                'Slicer plot: the list of dims to be kept cannot be empty.'
            )
        if not all(dim in ds.dims for dim in keep):
            raise ValueError(
                f"Slicer plot: one or more of the requested dims to be kept {keep} "
                f"were not found in the input's dimensions {ds.dims}."
            )

        if autoscale == 'fixed':
            if None not in (vmin, vmax):
                warnings.warn(
                    'Slicer plot: autoscale is set to "fixed", but vmin and vmax '
                    'are also specified. They will override the autoscale setting.',
                    RuntimeWarning,
                )
            if vmin is None:
                vmin = reduce(min, [da.data.min() for da in ds.values()])
            if vmax is None:
                vmax = reduce(max, [da.data.max() for da in ds.values()])
            autoscale = 'auto'  # Change back to something the figure understands

        from ..widgets import SliceWidget, slice_dims

        self.data_nodes = [Node(da) for da in ds.values()]

        self.slider = SliceWidget(ds, dims=[dim for dim in ds.dims if dim not in keep])
        self.slider_node = widget_node(self.slider)
        self.slice_nodes = [
            slice_dims(data_node, self.slider_node) for data_node in self.data_nodes
        ]
        ndims = len(keep)
        if ndims == 1:
            make_figure = figure1d
        elif ndims == 2:
            make_figure = figure2d
        else:
            raise ValueError(
                f'Slicer plot: the number of dims to be kept must be 1 or 2, '
                f'but {ndims} were requested.'
            )
        self.figure = make_figure(
            *self.slice_nodes,
            autoscale=autoscale,
            vmin=vmin,
            vmax=vmax,
            **kwargs,
        )


def slicer(
    obj: Union[VariableLike, ndarray, Dict[str, Union[VariableLike, ndarray]]],
    keep: List[str] = None,
    *,
    autoscale: Literal['auto', 'grow', 'fixed'] = 'auto',
    vmin: Union[VariableLike, int, float] = None,
    vmax: Union[VariableLike, int, float] = None,
    **kwargs,
):
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
    autoscale:
        The behavior of the y-axis (1d plots) and color range (2d plots) limits.
        If ``auto``, the limits automatically adjusts every time the data changes.
        If ``grow``, the limits are allowed to grow with time but they do not shrink.
        If ``fixed``, the limits are fixed to the full data range and do not change
        with time.
    vmin:
        The minimum value of the y-axis (1d plots) or color range (2d plots).
    vmax:
        The maximum value of the y-axis (1d plots) or color range (2d plots).
    **kwargs:
        See :py:func:`plopp.plot` for the full list of figure customization arguments.

    Returns
    -------
    :
        A :class:`Box` which will contain a :class:`Figure` and slider widgets.
    """
    require_interactive_backend('slicer')
    sl = Slicer(
        obj=obj,
        keep=keep,
        autoscale=autoscale,
        vmin=vmin,
        vmax=vmax,
        **kwargs,
    )
    from ..widgets import Box

    return Box([sl.figure, sl.slider])
