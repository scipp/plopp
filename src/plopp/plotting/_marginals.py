# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026 Scipp contributors (https://github.com/scipp)

from typing import Any, Literal

import matplotlib.pyplot as plt
import scipp as sc
from mpl_toolkits.axes_grid1 import make_axes_locatable

from ..backends.matplotlib.utils import make_figure
from ..core import Node
from ..core.typing import FigureLike
from ..graphics import imagefigure, linefigure


def marginals_plot(
    data: sc.DataArray | Node,
    *,
    side: Literal["left", "right"] = "left",
    title: str = "",
    ax: plt.Axes | None = None,
    **plot_kwargs: Any,
) -> FigureLike:
    """Plot 2D data and the sums over each dim as a 1D plot.

    This function plots ``data`` as a 2D image with a colorbar.
    It also sums over each of its dimensions and plots the resulting 1D data
    next to and above the main image.

    .. versionadded:: 26.11.0

    Parameters
    ----------
    data:
        The data to plot. Must be 2-dimensional.
    side:
        Which side to show the 1D plot along the y-axis.
        Note that when ``side == "left"``, the x-axis of the side plot is inverted,
        i.e., it increases from right to left.
    title:
        Title of the plot.
    ax:
        Optional axes to plot into. If None, ``marginals_plot`` creates new Axes.
    **plot_kwargs:
        Forwarded to *all* subplots :func:`plopp.graphics.linefigure`,
        and :func:`plopp.graphics.imagefigure`.

    Returns
    -------
    :
        A figure that contains all axes.
    """
    if ax is None:
        ax_2d = make_figure().subplots()
    else:
        ax_2d = ax

    divider = make_axes_locatable(ax_2d)
    ax_top = divider.append_axes("top", 1.2, pad=0.1, sharex=ax_2d)
    ax_side = divider.append_axes(side, 1.2, pad=0.1, sharey=ax_2d)
    cax = divider.append_axes("right", "4%", pad="5%")

    main_data_node = data if isinstance(data, Node) else Node(data)
    fig = imagefigure(main_data_node, ax=ax_2d, cax=cax, cbar=True, **plot_kwargs)

    # Main plot (2D)
    y_label = ax_2d.get_ylabel()
    if side == "left":
        ax_2d.yaxis.set_tick_params(labelleft=False)
        ax_2d.set_ylabel("")

    # Top Plot
    top_node = Node(lambda da: da.sum(da.dims[0]), main_data_node)
    linefigure(top_node, ax=ax_top, title=title, **plot_kwargs)
    ax_top.xaxis.set_tick_params(labelbottom=False)
    ax_top.set_xlabel("")

    # Side plot
    def make_side_data(da: sc.DataArray) -> sc.DataArray:
        summed = da.sum(da.dims[1])
        return sc.DataArray(
            data=summed.coords[summed.dim],
            # rename to work around https://github.com/scipp/plopp/issues/616.
            coords={summed.dim: summed.data},
        ).rename({summed.dim: " "})

    side_node = Node(make_side_data, main_data_node)
    linefigure(side_node, ax=ax_side, **plot_kwargs)
    ax_side.set_xlabel(ax_top.get_ylabel())
    if side == "left":
        ax_side.set_ylabel(y_label)
        ax_side.invert_xaxis()
    else:
        ax_side.yaxis.set_tick_params(labelleft=False)
        ax_side.set_ylabel("")

    return fig
