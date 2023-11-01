# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from __future__ import annotations

from typing import Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec

from ..protocols import FigureLike
from .static import get_repr_maker
from .utils import copy_figure, is_interactive_backend, silent_mpl_figure

from . import _make_figure


def residual(main_fig, reference):
    with silent_mpl_figure():
        fig = plt.figure(figsize=(6.0, 4.0))
    main_ax = fig.add_axes([0.1, 0.3, 1.0, 0.7])
    res_ax = fig.add_axes([0.1, 0.0, 1.0, 0.3])
    main_view = copy_figure(main_fig, ax=main_ax)
    ref_node = next(iter(reference._view.graph_nodes.values()))
    ref_node.add_view(main_view)
    main_view._view.render()
    diff_nodes = [n - ref_node for n in main_fig._view.graph_nodes.values()]
    res_view = reference.__class__(reference._view.__class__, *diff_nodes, ax=res_ax)

    return main_view
