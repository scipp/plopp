# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import warnings
from itertools import groupby
from functools import reduce
from typing import Dict, List, Literal, Optional, Union

import scipp as sc
from numpy import ndarray
from scipp.typing import VariableLike

from ..core import Node, widget_node
from ..core.typing import PlottableMulti
from ..graphics import figure1d, figure2d
from .common import inputs_to_nodes, require_interactive_backend


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
    coords:
        If supplied, use these coords instead of the input's dimension coordinates.
    vmin:
        The minimum value of the y-axis (1d plots) or color range (2d plots).
    vmax:
        The maximum value of the y-axis (1d plots) or color range (2d plots).
    **kwargs:
        The additional arguments are forwarded to the underlying 1D or 2D figures.
    """

    def __init__(
        self,
        *inputs: PlottableMulti,
        keep: List[str] = None,
        autoscale: Literal['auto', 'grow', 'fixed'] = 'auto',
        coords: Optional[List[str]] = None,
        vmin: Union[VariableLike, int, float] = None,
        vmax: Union[VariableLike, int, float] = None,
        **kwargs,
    ):
        # data_arrays = preprocess_multi(obj, ignore_size=True)
        # ds = sc.Dataset({da.name: da for da in data_arrays})

        # flat_inputs = []
        # for inp in inputs:
        #     if isinstance(inp, dict):
        #         flat_inputs.extend(inp.items())
        #     else:
        #         flat_inputs.append(('', inp))
        # nodes = [
        #     Node(preprocess, inp, name=name, ignore_size=True, coords=coords)
        #     for name, inp in flat_inputs
        # ]
        nodes = inputs_to_nodes(*inputs, ignore_size=True, coords=coords)

        # Ensure all inputs have the same sizes
        sizes = [node().sizes for node in nodes]
        g = groupby(sizes)
        if not (next(g, True) and not next(g, False)):
            raise ValueError(
                'Slicer plot: all inputs must have the same sizes, but '
                f'the following sizes were found: {sizes}'
            )

        # data = nodes[0]()
        dims = tuple(sizes[0])
        if keep is None:
            keep = dims[-(2 if len(dims) > 2 else 1) :]

        if isinstance(keep, str):
            keep = [keep]

        if len(keep) == 0:
            raise ValueError(
                'Slicer plot: the list of dims to be kept cannot be empty.'
            )
        if not all(dim in dims for dim in keep):
            raise ValueError(
                f"Slicer plot: one or more of the requested dims to be kept {keep} "
                f"were not found in the input's dimensions {dims}."
            )

        if autoscale == 'fixed':
            if None not in (vmin, vmax):
                warnings.warn(
                    'Slicer plot: autoscale is set to "fixed", but vmin and vmax '
                    'are also specified. They will override the autoscale setting.',
                    RuntimeWarning,
                )
            if vmin is None:
                vmin = reduce(min, [node().data.min() for node in nodes])
            if vmax is None:
                vmax = reduce(max, [node().data.max() for node in nodes])
            autoscale = 'auto'  # Change back to something the figure understands

        from ..widgets import SliceWidget, slice_dims

        # self.data_nodes = [Node(da) for da in ds.values()]

        self.slider = SliceWidget(
            nodes[0](), dims=[dim for dim in dims if dim not in keep]
        )
        self.slider_node = widget_node(self.slider)
        self.slice_nodes = [slice_dims(node, self.slider_node) for node in nodes]

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
    *inputs: PlottableMulti,
    keep: List[str] = None,
    autoscale: Literal['auto', 'grow', 'fixed'] = 'auto',
    coords: Optional[List[str]] = None,
    vmin: Union[VariableLike, int, float] = None,
    vmax: Union[VariableLike, int, float] = None,
    **kwargs,
):
    """
    Plot a multi-dimensional object by slicing one or more of the dimensions.
    This will produce one slider per sliced dimension, below the figure.

    Parameters
    ----------
    inputs:
        The data objects to be plotted.
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
    coords:
        If supplied, use these coords instead of the input's dimension coordinates.
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
        *inputs,
        keep=keep,
        autoscale=autoscale,
        vmin=vmin,
        vmax=vmax,
        coords=coords,
        **kwargs,
    )
    from ..widgets import Box

    return Box([sl.figure, sl.slider])
