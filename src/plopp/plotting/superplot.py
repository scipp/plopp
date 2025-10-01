# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from ..core.typing import FigureLike, Plottable
from .signature import with_1d_plot_params
from .slicer import Slicer


@with_1d_plot_params()
def superplot(
    obj: Plottable,
    keep: str | None = None,
    **kwargs,
) -> FigureLike:
    """
    Plot a multi-dimensional object as a one-dimensional line, slicing all but one
    dimension. This will produce one slider per sliced dimension, below the figure.
    In addition, a tool for saving the currently displayed line is added on the right
    hand side of the figure.

    Parameters
    ----------
    obj:
        The object to be plotted.
    keep:
        The single dimension to be kept, all remaining dimensions will be sliced.
        This should be a single string. If no dim is provided, the last/inner dim will
        be kept.

    Returns
    -------
    :
        A :class:`widgets.Box` which will contain a :class:`graphics.FigLine`, slider
        widgets and a tool to save/delete lines.
    """
    from ..widgets import LineSaveTool

    slicer = Slicer(obj, keep=keep, **kwargs)
    slicer.figure.right_bar.add(
        LineSaveTool(
            data_node=slicer.slice_nodes[0],
            slider_node=slicer.slider_node,
            fig=slicer.figure,
        )
    )
    return slicer.figure
