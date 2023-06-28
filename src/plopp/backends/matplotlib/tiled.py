# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from typing import Literal, Optional, Tuple, Union

from matplotlib import gridspec

import matplotlib.pyplot as plt

# import numpy as np
# import scipp as sc
# from matplotlib.collections import QuadMesh
# from mpl_toolkits.axes_grid1 import make_axes_locatable

from .utils import silent_mpl_figure


class Tiled:
    def __init__(self, nrows: int, ncols: int, figsize=None, **kwargs):
        self.nrows = nrows
        self.ncols = ncols
        with silent_mpl_figure():
            self.fig = plt.figure(
                layout="constrained",
                figsize=(min(6.0 * ncols, 15.0), min(4.0 * nrows, 15.0))
                if figsize is None
                else figsize,
            )
        self.gs = gridspec.GridSpec(nrows, ncols, figure=self.fig, **kwargs)
        self.axes = []

    def __setitem__(self, inds, view):
        ax = self.fig.add_subplot(self.gs[inds])
        if view.canvas.title:
            ax.set_title(view.canvas.title)
        ax.grid(view.canvas.grid)
        view.canvas.clear()
        view.canvas.ax = ax
        # with silent_mpl_figure():
        #     view.canvas.fig = plt.figure()
        # view.canvas.fig.add_axes(ax)
        self.axes.append(ax)
        view.artists.clear()
        for key, n in view.graph_nodes.items():
            view.update(n(), key=key)
