# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from functools import partial
from itertools import groupby
from typing import Literal

import scipp as sc

from ..core import widget_node
from ..core.typing import FigureLike, PlottableMulti
from ..graphics import imagefigure, linefigure
from .common import (
    input_to_nodes,
    preprocess,
    raise_multiple_inputs_for_2d_plot_error,
    require_interactive_figure,
)
from .plot import categorize_args


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
        **kwargs,
    ):
        nodes = input_to_nodes(
            obj,
            processor=partial(preprocess, ignore_size=True, coords=coords),
        )

        dims = nodes[0]().dims
        if keep is None:
            keep = dims[-(2 if len(dims) > 2 else 1) :]

        if isinstance(keep, str):
            keep = [keep]

        # Ensure all dims in keep have the same size
        sizes = [
            {dim: shape for dim, shape in node().sizes.items() if dim not in keep}
            for node in nodes
        ]
        g = groupby(sizes)
        if not (next(g, True) and not next(g, False)):
            raise ValueError(
                'Slicer plot: all inputs must have the same sizes, but '
                f'the following sizes were found: {sizes}'
            )

        if len(keep) == 0:
            raise ValueError(
                'Slicer plot: the list of dims to be kept cannot be empty.'
            )
        if not all(dim in dims for dim in keep):
            raise ValueError(
                f"Slicer plot: one or more of the requested dims to be kept {keep} "
                f"were not found in the input's dimensions {dims}."
            )

        from ..widgets import SliceWidget, slice_dims

        self.slider = SliceWidget(
            nodes[0](),
            dims=[dim for dim in dims if dim not in keep],
            enable_player=enable_player,
        )
        self.slider_node = widget_node(self.slider)
        self.slice_nodes = [slice_dims(node, self.slider_node) for node in nodes]

        args = categorize_args(**kwargs)

        ndims = len(keep)
        if ndims == 1:
            make_figure = partial(linefigure, **args['1d'])
        elif ndims == 2:
            if len(self.slice_nodes) > 1:
                raise_multiple_inputs_for_2d_plot_error(origin='slicer')
            make_figure = partial(imagefigure, **args['2d'])
        else:
            raise ValueError(
                f'Slicer plot: the number of dims to be kept must be 1 or 2, '
                f'but {ndims} were requested.'
            )

        self.figure = make_figure(*self.slice_nodes)
        require_interactive_figure(self.figure, 'slicer')
        self.figure.bottom_bar.add(self.slider)


def slicer(
    obj: PlottableMulti,
    keep: list[str] | None = None,
    *,
    aspect: Literal['auto', 'equal', None] = None,
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
    mask_color: str = 'black',
    nan_color: str | None = None,
    norm: Literal['linear', 'log', None] = None,
    scale: dict[str, str] | None = None,
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
    mask_color:
        Color of masks in 1d plots.
    nan_color:
        Color to use for NaN values in 2d plots.
    norm:
        Set to ``'log'`` for a logarithmic y-axis (1d plots) or logarithmic colorscale
        (2d plots). Legacy, prefer ``logy`` and ``logc`` instead.
    scale:
        Change axis scaling between ``log`` and ``linear``. For example, specify
        ``scale={'tof': 'log'}`` if you want log-scale for the ``tof`` dimension.
        Legacy, prefer ``logx`` and ``logy`` instead.
    title:
        The figure title.
    vmax:
        Upper bound for data to be displayed (y-axis for 1d plots, colorscale for
        2d plots). Legacy, prefer ``ymax`` and ``cmax`` instead.
    vmin:
        Lower bound for data to be displayed (y-axis for 1d plots, colorscale for
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
    return Slicer(
        obj,
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
        nan_color=nan_color,
        norm=norm,
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
