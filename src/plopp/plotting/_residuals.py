# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026 Scipp contributors (https://github.com/scipp)

from functools import partial
from typing import Any, Literal

import matplotlib.pyplot as plt
import scipp as sc
from mpl_toolkits.axes_grid1 import make_axes_locatable

from ..backends.matplotlib.utils import make_figure
from ..core import Node
from ..core.typing import FigureLike, Plottable, PlottableMulti
from ..graphics import imagefigure, linefigure
from .common import input_to_nodes, preprocess


def residuals(
    obj: PlottableMulti,
    *,
    reference: Plottable,
    title: str = "",
    ax: plt.Axes | None = None,
    rax: plt.Axes | None = None,
    ignore_size: bool = False,
    ignore_sorted: bool = False,
    coords=None,
    **plot_kwargs: Any,
) -> FigureLike:
    """ """
    if ax is None:
        main_ax = make_figure().subplots()
    else:
        main_ax = ax

    divider = make_axes_locatable(main_ax)
    res_ax = (
        divider.append_axes("bottom", "10%", pad=0, sharex=main_ax)
        if rax is None
        else rax
    )

    main_data_node = input_to_nodes(
        obj,
        processor=partial(
            preprocess,
            ignore_size=ignore_size,
            ignore_sorted=ignore_sorted,
            coords=coords,
        ),
    )
    reference_node = input_to_nodes(
        reference,
        processor=partial(
            preprocess,
            ignore_size=ignore_size,
            ignore_sorted=ignore_sorted,
            coords=coords,
        ),
    )
    if len(reference_node) > 1:
        raise ValueError("The residuals plot accepts only a single reference input.")
    reference_node = reference_node[0]

    fig = imagefigure(main_data_node, ax=ax_2d, cax=cax, cbar=cbar, **plot_kwargs)

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
        if da.coords.is_edges(da.dims[0]):
            raise sc.DimensionError(
                "marginals() does not support bin edges along the y-axis."
            )
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
