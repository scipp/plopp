# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from functools import partial
from typing import Literal

import numpy as np
import scipp as sc

from ..core import Node, widget_node
from ..core.typing import FigureLike, PlottableMulti
from ..graphics import imagefigure, linefigure
from ..widgets import CombinedSliceWidget, RangeSliceWidget, SliceWidget, slice_dims
from .common import (
    categorize_args,
    input_to_nodes,
    preprocess,
    raise_multiple_inputs_for_2d_plot_error,
    require_interactive_figure,
)


def _maybe_reduce_dim(da, dims, op):
    to_be_reduced = set(dims) & set(da.dims)

    # Small optimization: squeezing is much faster than reducing
    to_be_squeezed = {dim for dim in to_be_reduced if da.sizes[dim] == 1}
    if to_be_squeezed:
        da = da.squeeze()
        to_be_reduced -= to_be_squeezed

    if not to_be_reduced:
        return da

    if 'mean' not in op:
        return getattr(da, op)(to_be_reduced)

    # If the operation is a mean, there is currently a bug in the implementation
    # in scipp where doing a mean over a subset of the array's dimensions gives the
    # wrong result: https://github.com/scipp/scipp/issues/3841
    # Instead, we manually compute the mean
    if 'nan' in op:
        numerator = da.nansum(to_be_reduced)
        denominator = (~sc.isnan(da)).to(dtype=int).sum(to_be_reduced)
        denominator.unit = ""
    else:
        numerator = da.sum(to_be_reduced)
        denominator = np.prod([da.sizes[dim] for dim in to_be_reduced])
    return numerator / denominator


class DimensionSlicer:
    """
    Class that slices out dimensions from the input data and exposes the result in
    'output' nodes.

    This class exists both for simplifying unit tests and for reuse by other plotting
    functions that want to offer slicing functionality,
    such as the :func:`superplot` function.

    Parameters
    ----------
    obj:
        The input data.
    enable_player:
        If ``True``, add a play button to the sliders to automatically step through
        the slices.
    keep:
        The dimensions to be kept, all remaining dimensions will be sliced. This should
        be a list of dims. If no dims are provided, the last dim will be kept in the
        case of a 2-dimensional input, while the last two dims will be kept in the case
        of higher dimensional inputs.
    mode:
        The mode of the slicer. This can be 'single', 'range', or 'combined'.
    operation:
        The reduction operation to be applied to the sliced dimensions. This is ``sum``
        by default.
    """

    def __init__(
        self,
        obj: PlottableMulti | list[Node] | tuple[Node, ...],
        *,
        enable_player: bool = False,
        keep: list[str] | None = None,
        mode: Literal['single', 'range', 'combined'] = 'combined',
        operation: Literal[
            'sum', 'mean', 'max', 'min', 'nansum', 'nanmean', 'nanmax', 'nanmin'
        ] = 'sum',
    ):
        if enable_player and mode != 'single':
            raise ValueError(
                'The play button cannot be used with range sliders. Please set '
                'mode to "single" to use the play button.'
            )
        if isinstance(obj, list | tuple) and ({type(x) for x in obj} == {Node}):
            nodes = obj
        else:
            nodes = input_to_nodes(obj, processor=lambda x, name: x)

        # Ensure all inputs have the same dims
        dg = sc.DataGroup({str(i): node() for i, node in enumerate(nodes)})
        dg_dims = set(dg.dims)
        if not all(set(da.dims) == dg_dims for da in dg.values()):
            raise ValueError(
                'Slicer plot: all inputs must have the same dimensions, but the '
                f'following dimensions were found: {[da.dims for da in dg.values()]}'
            )

        self.keep = keep
        if self.keep is None:
            self.keep = dg.dims[-min(dg.ndim - 1, 2) :]
        if isinstance(self.keep, str):
            self.keep = [self.keep]

        if len(self.keep) == 0:
            raise ValueError(
                'Slicer plot: the list of dims to be kept cannot be empty.'
            )
        if not set(self.keep).issubset(dg_dims):
            raise ValueError(
                "Slicer plot: one or more of the requested dims to be kept "
                f"{self.keep} were not found in the input's dimensions {dg.dims}."
            )

        other_dims = [dim for dim in dg.dims if dim not in self.keep]
        data_arrays = list(dg.values())
        # Ensure all dims in other_dims (dims to be sliced) have the same coordinates
        if len(dg) > 1:
            for dim in other_dims:
                template = data_arrays[0]
                for da in data_arrays[1:]:
                    if not sc.identical(da.coords[dim], template.coords[dim]):
                        raise ValueError(
                            f"Slicer plot: cannot slice dim '{dim}' because all inputs "
                            "do not have the same coordinates for this dim."
                        )

        match mode:
            case 'single':
                slicer_constr = SliceWidget
            case 'range':
                slicer_constr = RangeSliceWidget
            case 'combined':
                slicer_constr = CombinedSliceWidget
            case _:
                raise ValueError(
                    f"Invalid mode: {mode}. Expected one of 'single', "
                    f"'range', or 'combined'."
                )

        self.slider = slicer_constr(
            data_arrays[0], dims=other_dims, enable_player=enable_player
        )
        self.slider_node = widget_node(self.slider)
        self.slice_nodes = [slice_dims(node, self.slider_node) for node in nodes]
        self.reduce_nodes = [
            Node(_maybe_reduce_dim, da=node, dims=other_dims, op=operation)
            for node in self.slice_nodes
        ]

    @property
    def output(self) -> list[Node] | Node:
        """
        Alias for ``reduce_nodes`` whose name is more like an implementation detail.
        We keep the ``reduce_nodes`` attribute for retro-compatibility.
        """
        if len(self.reduce_nodes) == 1:
            return self.reduce_nodes[0]
        return self.reduce_nodes


class SlicerPlot:
    """
    Initialize a SlicerPlot, which contains both a Slicer that slices extra
    dimensions of the input data, and a figure that displays the result as
    either a 1D line or a 2D image.

    Parameters
    ----------
    obj:
        The input data.
    coords:
        If supplied, use these coords instead of the input's dimension coordinates.
    enable_player:
        If ``True``, add a play button to the sliders to automatically step through
        the slices.
    keep:
        The dimensions to be kept, all remaining dimensions will be sliced. This should
        be a list of dims. If no dims are provided, the last dim will be kept in the
        case of a 2-dimensional input, while the last two dims will be kept in the case
        of higher dimensional inputs.
    mode:
        The mode of the slicer. This can be 'single', 'range', or 'combined'.
    operation:
        The reduction operation to be applied to the sliced dimensions. This is ``sum``
        by default.
    **kwargs:
        The additional arguments are forwarded to the underlying 1D or 2D figures.
    """

    def __init__(
        self,
        obj: PlottableMulti,
        *,
        coords: list[str] | None = None,
        enable_player: bool = False,
        keep: list[str] | None = None,
        mode: Literal['single', 'range', 'combined'] = 'combined',
        operation: Literal[
            'sum', 'mean', 'max', 'min', 'nansum', 'nanmean', 'nanmax', 'nanmin'
        ] = 'sum',
        **kwargs,
    ):
        nodes = input_to_nodes(
            obj, processor=partial(preprocess, ignore_size=True, coords=coords)
        )

        self.slicer = DimensionSlicer(
            nodes,
            keep=keep,
            enable_player=enable_player,
            mode=mode,
            operation=operation,
        )

        args = categorize_args(**kwargs)

        ndims = len(self.slicer.keep)
        if ndims == 1:
            make_figure = partial(linefigure, **args['1d'])
        elif ndims == 2:
            if len(self.slicer.slice_nodes) > 1:
                raise_multiple_inputs_for_2d_plot_error(origin='slicer')
            make_figure = partial(imagefigure, **args['2d'])
        else:
            raise ValueError(
                f'Slicer plot: the number of dims to be kept must be 1 or 2, '
                f'but {ndims} were requested.'
            )

        self.figure = make_figure(*self.slicer.reduce_nodes)
        require_interactive_figure(self.figure, 'slicer')
        self.figure.bottom_bar.add(self.slicer.slider)


def slicer(
    obj: PlottableMulti,
    keep: list[str] | None = None,
    *,
    aspect: Literal['auto', 'equal'] | None = None,
    autoscale: bool = True,
    cbar: bool = True,
    clabel: str | None = None,
    cmap: str = 'viridis',
    cmax: sc.Variable | float | None = None,
    cmin: sc.Variable | float | None = None,
    coords: list[str] | None = None,
    enable_player: bool = False,
    errorbars: bool = True,
    figsize: tuple[float, float] | None = None,
    grid: bool = False,
    legend: bool | tuple[float, float] = True,
    logc: bool | None = None,
    logx: bool | None = None,
    logy: bool | None = None,
    mask_cmap: str = 'gray',
    mask_color: str | None = None,
    nan_color: str | None = None,
    norm: Literal['linear', 'log'] | None = None,
    operation: Literal[
        'sum', 'mean', 'max', 'min', 'nansum', 'nanmean', 'nanmax', 'nanmin'
    ] = 'sum',
    scale: dict[str, str] | None = None,
    mode: Literal['single', 'range', 'combined'] = 'combined',
    title: str | None = None,
    vmax: sc.Variable | float | None = None,
    vmin: sc.Variable | float | None = None,
    xlabel: str | None = None,
    xmax: sc.Variable | float | None = None,
    xmin: sc.Variable | float | None = None,
    ylabel: str | None = None,
    ymax: sc.Variable | float | None = None,
    ymin: sc.Variable | float | None = None,
    **kwargs,
) -> FigureLike:
    """
    Plot a multi-dimensional object by slicing one or more of the dimensions.
    This will produce one slider per sliced dimension, below the figure.

    Parameters
    ----------
    obj:
        The object to be plotted.
    keep:
        The single dimension to be kept, all remaining dimensions will be sliced.
        This should be a single string. If no dim is provided, the last/inner dim will
        be kept.
    aspect:
        Aspect ratio for the axes.
    autoscale:
        Automatically scale the axes/colormap on updates if ``True``.
    cbar:
        Show colorbar in 2d plots if ``True``.
    clabel:
        Label for colorscale (2d plots only).
    cmap:
        The colormap to be used for the colorscale (2d plots only).
    cmax:
        Upper limit for colorscale (2d plots only).
    cmin:
        Lower limit for colorscale (2d plots only).
    coords:
        If supplied, use these coords instead of the input's dimension coordinates.
    enable_player:
        If ``True``, add a play button to the sliders to automatically step through
        the slices.
    errorbars:
        Show errorbars in 1d plots if ``True``.
    figsize:
        The width and height of the figure, in inches.
    grid:
        Show grid if ``True``.
    legend:
        Show legend if ``True``. If ``legend`` is a tuple, it should contain the
        ``(x, y)`` coordinates of the legend's anchor point in axes coordinates.
    logc:
        If ``True``, use logarithmic scale for colorscale (2d plots only).
    logx:
        If ``True``, use logarithmic scale for x-axis.
    logy:
        If ``True``, use logarithmic scale for y-axis.
    mask_cmap:
        Colormap to use for masks in 2d plots.
    mask_color:
        Color of masks.
    mode:
        The type of slider to use for slicing. Can be either ``'single'`` for sliders
        that select a single index along the sliced dimension, ``'range'`` for sliders
        that select a range of indices along the sliced dimension, or ``'combined'`` for
        sliders that allow both single index selection and range selection.
        Defaults to ``'combined'``.
    nan_color:
        Color to use for NaN values in 2d plots.
    norm:
        Set to ``'log'`` for a logarithmic y-axis (1d plots) or logarithmic colorscale
        (2d plots). Legacy, prefer ``logy`` and ``logc`` instead.
    operation:
        The reduction operation to be applied to the sliced dimensions. This is ``sum``
        by default.
    scale:
        Change axis scaling between ``log`` and ``linear``. For example, specify
        ``scale={'time': 'log'}`` if you want log-scale for the ``time`` dimension.
        Legacy, prefer ``logx`` and ``logy`` instead.
    title:
        The figure title.
    vmax:
        Upper limit for data to be displayed (y-axis for 1d plots, colorscale for
        2d plots). Legacy, prefer ``ymax`` and ``cmax`` instead.
    vmin:
        Lower limit for data to be displayed (y-axis for 1d plots, colorscale for
        2d plots). Legacy, prefer ``ymin`` and ``cmin`` instead.
    xlabel:
        Label for x-axis.
    xmax:
        Upper limit for x-axis.
    xmin:
        Lower limit for x-axis.
    ylabel:
        Label for y-axis.
    ymax:
        Upper limit for y-axis.
    ymin:
        Lower limit for y-axis.
    **kwargs:
        Additional arguments forwarded to the underlying plotting library.
    """
    return SlicerPlot(
        obj=obj,
        keep=keep,
        aspect=aspect,
        autoscale=autoscale,
        cbar=cbar,
        clabel=clabel,
        cmap=cmap,
        cmax=cmax,
        cmin=cmin,
        coords=coords,
        enable_player=enable_player,
        errorbars=errorbars,
        figsize=figsize,
        grid=grid,
        legend=legend,
        logc=logc,
        logx=logx,
        logy=logy,
        mask_color=mask_color,
        mask_cmap=mask_cmap,
        mode=mode,
        nan_color=nan_color,
        norm=norm,
        operation=operation,
        scale=scale,
        title=title,
        vmax=vmax,
        vmin=vmin,
        xlabel=xlabel,
        xmax=xmax,
        xmin=xmin,
        ylabel=ylabel,
        ymax=ymax,
        ymin=ymin,
        **kwargs,
    ).figure
