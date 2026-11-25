# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026 Scipp contributors (https://github.com/scipp)

from functools import partial
from typing import Any, Literal

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

from ..backends.matplotlib.utils import make_figure
from ..core.typing import FigureLike, Plottable, PlottableMulti
from ..graphics import linefigure
from .common import input_to_nodes, preprocess


def residuals(
    obj: PlottableMulti,
    *,
    reference: Plottable,
    mode: Literal["absolute", "relative", "abs", "rel"] = "absolute",
    ax: plt.Axes | None = None,
    rax: plt.Axes | None = None,
    ignore_size: bool = False,
    ignore_sorted: bool = False,
    coords=None,
    **plot_kwargs: Any,
) -> FigureLike:
    """ """

    if "abs" not in mode and "rel" not in mode:
        raise ValueError(f"Invalid mode: {mode}")

    if ax is None:
        main_ax = make_figure().subplots()
    else:
        main_ax = ax

    divider = make_axes_locatable(main_ax)
    res_ax = (
        divider.append_axes("bottom", "20%", pad="3%", sharex=main_ax)
        if rax is None
        else rax
    )

    main_ax.tick_params(
        axis='x',
        which='both',
        bottom=True,
        top=False,
        labelbottom=False,
        direction='in',
    )
    main_ax_top = main_ax.secondary_xaxis('top')
    main_ax_top.tick_params(axis='x', which='both', direction='out', labeltop=True)

    res_ax.tick_params(
        axis='x',
        which='both',
        bottom=True,
        top=False,
        labelbottom=True,
        direction='out',
    )
    res_ax_top = res_ax.secondary_xaxis('top')
    res_ax_top.tick_params(axis='x', which='both', direction='in', labeltop=False)

    main_data_nodes = input_to_nodes(
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

    diff_nodes = [
        a - reference_node
        if mode in ("absolute", "abs")
        else (a - reference_node) / reference_node
        for a in main_data_nodes
    ]

    main_fig = linefigure(
        *[*main_data_nodes, reference_node], ax=main_ax, **plot_kwargs
    )
    main_fig.canvas._logx_button.alpha = 0.0
    linefigure(*diff_nodes, ax=res_ax, **plot_kwargs)
    res_ax.axhline(0, color='gray', linestyle='--', linewidth=1)
    main_ax.set_xlabel('')

    return main_fig
