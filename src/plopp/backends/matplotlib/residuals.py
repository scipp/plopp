# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import matplotlib.pyplot as plt

from ..protocols import FigureLike
from .utils import copy_figure, make_figure


class ResidualPlot:
    def __init__(self, main_panel: FigureLike, res_panel: FigureLike):
        self.main_panel = main_panel
        self.res_panel = res_panel
        self.panels = [self.main_panel, self.res_panel]

    def __getitem__(self, key):
        return self.panels[key]

    def __repr__(self):
        return f"ResidualPlot(main_panel={self.main_panel}, res_panel={self.res_panel})"

    def _repr_mimebundle_(self, *args, **kwargs) -> dict:
        return self.main_panel._repr_mimebundle_(*args, **kwargs)


def residuals(main_fig: FigureLike, reference: FigureLike) -> ResidualPlot:
    """
    Create a residual plot from two figures, using the data from the second figure as
    the reference the residuals are computed from.

    Parameters
    ----------
    main_fig:
        The main figure.
    reference:
        The reference figure.

    Returns
    -------
    :
        A figure with a main panel showing the data from both the main and reference
        figures, and a smaller 'residuals' panel at the bottom displaying the difference
        between the data from the main figure with the data from the reference figure.
    """
    # If there is a colormapper, we are dealing with a 2d figure
    if hasattr(main_fig._view, 'colormapper') or hasattr(
        reference._view, 'colormapper'
    ):
        raise TypeError("The residual plot only supports 1d figures.")
    if len(reference.artists) != 1:
        raise TypeError(
            "The reference figure must contain exactly one line to "
            "compute residuals."
        )

    fig = make_figure(figsize=(6.0, 4.0))
    gs = fig.add_gridspec(
        2,
        1,
        height_ratios=(4, 1),
        hspace=0.0,
    )

    main_ax = fig.add_subplot(gs[0])
    res_ax = fig.add_subplot(gs[1], sharex=main_ax)
    main_panel = copy_figure(main_fig, ax=main_ax)
    main_canvas = main_panel.canvas
    if main_canvas.is_widget():
        fig.canvas.toolbar_visible = False
        fig.canvas.header_visible = False
    ref_node = next(iter(reference.graph_nodes.values()))
    data = ref_node()
    if not data.name:
        data.name = "reference"
    ref_node.add_view(main_panel)
    main_panel._view.render()
    # main_view._view.artists[ref_node.id]._line.set_zorder(-10)
    if main_canvas._legend:
        main_ax.legend()
    diff_nodes = [n - ref_node for n in main_fig.graph_nodes.values()]
    res_panel = reference.__class__(reference._view.__class__, *diff_nodes, ax=res_ax)

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

    return ResidualPlot(main_panel=main_panel, res_panel=res_panel)
