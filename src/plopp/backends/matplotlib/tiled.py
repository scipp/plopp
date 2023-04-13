# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from typing import Literal, Optional, Tuple, Union

from matplotlib import gridspec

# import matplotlib.pyplot as plt
# import numpy as np
# import scipp as sc
# from matplotlib.collections import QuadMesh
# from mpl_toolkits.axes_grid1 import make_axes_locatable


class Tiled:
    def __init__(self, nrows: int, ncols: int, **kwargs):
        self.nrows = nrows
        self.ncols = ncols
        self.gs = gridspec.GridSpec(nrows, ncols, **kwargs)
        self.axes = []

    def __setitem__(self, inds, view):
        ax = self.view.fig.add_subplot(self.gs[inds])
        view.canvas.ax = ax
        view.artists.clear()
        for key, n in view.graph_nodes.items():
            view.update(n(), key=key)
