# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core.limits import find_limits, fix_empty_range
from ..core.utils import number_to_variable
from .utils import fig_to_bytes, silent_mpl_figure

import matplotlib.pyplot as plt
from matplotlib.collections import QuadMesh
import numpy as np
import scipp as sc
from typing import Any, Tuple


def _none_if_not_finite(x):
    return x if np.isfinite(x) else None


class Canvas:

    def __init__(self,
                 ax: Any = None,
                 figsize: Tuple[float, ...] = None,
                 title: str = None,
                 grid: bool = False,
                 vmin=None,
                 vmax=None,
                 aspect='auto',
                 scale=None,
                 cbar=False):

        self.fig = None
        self.ax = ax
        self._user_vmin = vmin
        self._user_vmax = vmax
        self._scale = {} if scale is None else scale

        if self.ax is None:
            if figsize is None:
                figsize = (6, 4)
            with silent_mpl_figure():
                self.fig = plt.figure(figsize=figsize, dpi=96)
            left = 0.11
            right = 0.9
            bottom = 0.11
            top = 0.95
            if cbar:
                cbar_width = 0.03
                cbar_gap = 0.04
                self.ax = self.fig.add_axes(
                    [left, bottom, right - left - cbar_width - cbar_gap, top - bottom])
                self.cax = self.fig.add_axes(
                    [right - cbar_width, bottom, cbar_width, top - bottom])
            else:
                self.ax = self.fig.add_axes([left, bottom, right - left, top - bottom])
                self.cax = None
            if hasattr(self.fig.canvas, "on_widget_constructed"):
                self.fig.canvas.toolbar_visible = False
                self.fig.canvas.header_visible = False
        else:
            self.fig = self.ax.get_figure()

        self.ax.set_aspect(aspect)
        self.ax.set_title(title)
        self.ax.grid(grid)

        self._xmin = np.inf
        self._xmax = np.NINF
        self._ymin = np.inf
        self._ymax = np.NINF

    def to_image(self):
        from ipywidgets import Image
        bounds = self.fig.get_tightbbox(self.fig.canvas.get_renderer()).bounds
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        dpi = self.fig.get_dpi()
        return Image(value=fig_to_bytes(self.fig),
                     width=width * dpi,
                     height=height * dpi,
                     format='png')

    def autoscale(self, draw=True):
        """
        Matplotlib's autoscale only takes lines into account. We require a special
        handling for meshes, which is part of the axes collections.
        """
        if self.ax.lines:
            self.ax.relim()
            self.ax.autoscale()
            xmin, xmax = self.ax.get_xlim()
            ymin, ymax = self.ax.get_ylim()
            self._xmin = min(self._xmin, xmin)
            self._xmax = max(self._xmax, xmax)
            self._ymin = min(self._ymin, ymin)
            self._ymax = max(self._ymax, ymax)
        for c in self.ax.collections:
            if isinstance(c, QuadMesh):
                coords = c.get_coordinates()
                left, right = fix_empty_range(
                    find_limits(sc.array(dims=['x', 'y'], values=coords[..., 0]),
                                scale=self.xscale))
                bottom, top = fix_empty_range(
                    find_limits(sc.array(dims=['x', 'y'], values=coords[..., 1]),
                                scale=self.yscale))
                self._xmin = min(self._xmin, left.value)
                self._xmax = max(self._xmax, right.value)
                self._ymin = min(self._ymin, bottom.value)
                self._ymax = max(self._ymax, top.value)
        self.ax.set_xlim(_none_if_not_finite(self._xmin),
                         _none_if_not_finite(self._xmax))
        self.ax.set_ylim(_none_if_not_finite(self._ymin),
                         _none_if_not_finite(self._ymax))
        if draw:
            self.draw()

    def draw(self):
        self.fig.canvas.draw_idle()

    def savefig(self, filename: str, **kwargs):
        """
        Save plot to file.
        Possible file extensions are `.jpg`, `.png` and `.pdf`.
        The default directory for writing the file is the same as the
        directory where the script or notebook is running.
        """
        self.fig.savefig(filename, **{**{'bbox_inches': 'tight'}, **kwargs})

    def show(self):
        self.fig.show()

    def crop(self, **limits):
        for xy, lims in limits.items():
            getattr(self.ax, f'set_{xy}lim')(*[
                sc.to_unit(number_to_variable(lims[m]), unit=lims['unit']).value
                for m in ('min', 'max') if m in lims
            ])

    def legend(self):
        self.ax.legend()

    @property
    def xlabel(self):
        return self.ax.get_xlabel()

    @xlabel.setter
    def xlabel(self, lab):
        self.ax.set_xlabel(lab)

    @property
    def ylabel(self):
        return self.ax.get_ylabel()

    @ylabel.setter
    def ylabel(self, lab):
        self.ax.set_ylabel(lab)

    @property
    def xscale(self):
        return self.ax.get_xscale()

    @xscale.setter
    def xscale(self, scale):
        self.ax.set_xscale(scale)

    @property
    def yscale(self):
        return self.ax.get_yscale()

    @yscale.setter
    def yscale(self, scale):
        self.ax.set_yscale(scale)

    def reset_mode(self):
        self.fig.canvas.toolbar.mode = ''

    def zoom(self):
        self.fig.canvas.toolbar.zoom()

    def pan(self):
        self.fig.canvas.toolbar.pan()

    def save(self):
        self.fig.canvas.toolbar.save_figure()

    def logx(self):
        self.xscale = 'log' if self.xscale == 'linear' else 'linear'
        self._xmin = np.inf
        self._xmax = np.NINF
        self.autoscale()

    def logy(self):
        self.yscale = 'log' if self.yscale == 'linear' else 'linear'
        self._ymin = np.inf
        self._ymax = np.NINF
        self.autoscale()
