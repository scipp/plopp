# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import matplotlib.pyplot as plt

from ..protocols import FigureLike
from .utils import copy_figure, silent_mpl_figure


def residual(main_fig: FigureLike, reference: FigureLike) -> FigureLike:
    if hasattr(main_fig._view, 'colormapper') or hasattr(
        reference._view, 'colormapper'
    ):
        raise TypeError("The residual plot only supports 1d figures.")
    with silent_mpl_figure():
        fig = plt.figure(figsize=(6.0, 4.0))
    gs = fig.add_gridspec(
        2,
        1,
        height_ratios=(4, 1),
        hspace=0.0,
    )

    main_ax = fig.add_subplot(gs[0])
    res_ax = fig.add_subplot(gs[1], sharex=main_ax)
    main_view = copy_figure(main_fig, ax=main_ax)
    main_canvas = main_view._view.canvas
    if main_canvas.is_widget():
        fig.canvas.toolbar_visible = False
        fig.canvas.header_visible = False
    ref_node = next(iter(reference._view.graph_nodes.values()))
    data = ref_node()
    if not data.name:
        data.name = "reference"
    ref_node.add_view(main_view)
    main_view._view.render()
    # main_view._view.artists[ref_node.id]._line.set_zorder(-10)
    if main_canvas._legend:
        main_ax.legend()
    diff_nodes = [n - ref_node for n in main_fig._view.graph_nodes.values()]
    _ = reference.__class__(reference._view.__class__, *diff_nodes, ax=res_ax)

    main_ax.tick_params(
        top=True, labeltop=True, bottom=False, labelbottom=False, direction='out'
    )
    main_ax.secondary_xaxis("bottom").tick_params(
        axis="x",
        direction="in",
        top=False,
        labeltop=False,
        bottom=True,
        labelbottom=False,
    )
    res_ax.tick_params(
        top=False, labeltop=False, bottom=True, labelbottom=True, direction='out'
    )
    res_ax.secondary_xaxis("top").tick_params(
        axis="x",
        direction="in",
        top=True,
        labeltop=False,
        bottom=False,
        labelbottom=False,
    )

    return main_view
