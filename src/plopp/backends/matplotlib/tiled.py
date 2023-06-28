# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from typing import Literal, Optional, Tuple, Union

from matplotlib import gridspec
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colorbar import ColorbarBase
import numpy as np

# import numpy as np
# import scipp as sc
# from matplotlib.collections import QuadMesh
# from mpl_toolkits.axes_grid1 import make_axes_locatable

from .static import get_repr_maker
from .utils import silent_mpl_figure, is_interactive_backend


class Tiled:
    def __init__(self, nrows: int, ncols: int, figsize=None, **kwargs):
        self.nrows = nrows
        self.ncols = ncols
        with silent_mpl_figure():
            self.fig = plt.figure(
                figsize=(min(6.0 * ncols, 15.0), min(4.0 * nrows, 15.0))
                if figsize is None
                else figsize,
            )
        self.gs = gridspec.GridSpec(nrows, ncols, figure=self.fig, **kwargs)
        self.axes = []
        self.views = np.full((nrows, ncols), None)
        self._history = []

    def __setitem__(self, inds, view):
        ax = self.fig.add_subplot(self.gs[inds])

        if view.canvas.cax:
            divider = make_axes_locatable(ax)
            cax = divider.append_axes("right", "4%", pad="5%")
            cmapper = view._fig.colormapper
            cmapper.colorbar = ColorbarBase(
                cax, cmap=cmapper.cmap, norm=cmapper.normalizer
            )
            cax.yaxis.set_label_coords(-0.9, 0.5)
            cax.set_ylabel(cmapper.cax.get_ylabel())
            view.canvas.cax = cax
            cmapper.cax = cax

        if view.canvas.title:
            ax.set_title(view.canvas.title)
        ax.grid(view.canvas.grid)
        view.canvas.clear()
        view.canvas.ax = ax
        self.axes.append(ax)
        view.artists.clear()
        for key, n in view.graph_nodes.items():
            view.update(n(), key=key)
        self.views[inds] = view
        self.fig.tight_layout()
        self._history.append((inds, view))

    def __getitem__(self, inds):
        return self.views[inds]

    def _repr_mimebundle_(self, include=None, exclude=None) -> dict:
        """
        Mimebundle display representation for jupyter notebooks.
        """
        if is_interactive_backend():
            return self.fig.canvas._repr_mimebundle_(include=include, exclude=exclude)
        else:
            out = {'text/plain': 'TiledFigure'}
            npoints = sum(
                len(line.get_xdata()) for ax in self.axes for line in ax.lines
            )
            out.update(get_repr_maker(npoints=npoints)(self.fig))
            return out

    def save(self, filename: str, **kwargs):
        """
        Save the figure to file.
        The default directory for writing the file is the same as the
        directory where the script or notebook is running.

        Parameters
        ----------
        filename:
            Name of the output file. Possible file extensions are ``.jpg``, ``.png``,
            ``.svg``, and ``.pdf``.
        """
        self.fig.savefig(filename, **{**{'bbox_inches': 'tight'}, **kwargs})

    def show(self):
        """
        Make a call to Matplotlib's underlying ``show`` function.
        """
        self.fig.show()

    def __add__(self, other):
        if not isinstance(other, self.__class__):
            t = self.__class__(1, 1)
            t[0, 0] = other
            other = t

        out = Tiled(nrows=max(self.nrows, other.nrows), ncols=self.ncols + other.ncols)
        for inds, view in self._history:
            out[inds] = view
        for inds, view in other._history:
            out[inds[0], inds[1] + self.ncols] = view
        return out
