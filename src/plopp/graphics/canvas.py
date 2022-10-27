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
    """
    Matplotlib-based canvas used to render 2D graphics.
    It provides a figure and some axes, as well as functions for controlling the zoom,
    panning, and the scale of the axes.

    Parameters
    ----------
    ax:
        If supplied, use these axes to create the figure. If none are supplied, the
        canvas will create its own axes.
    figsize:
        The width and height of the figure, in inches.
    title:
        The title to be placed above the figure.
    grid:
        Display the figure grid if ``True``.
    vmin:
        The minimum value for the vertical axis.
    vmax:
        The maximum value for the vertical axis.
    aspect:
        The aspect ratio for the axes.
    scale:
        Change axis scaling between ``log`` and ``linear``. For example, specify
        ``scale={'tof': 'log'}`` if you want log-scale for the ``tof`` dimension.
    cbar:
        Add axes to host a colorbar if ``True``.
    """

    def __init__(self,
                 ax: plt.Axes = None,
                 figsize: Tuple[float, ...] = None,
                 title: str = None,
                 grid: bool = False,
                 vmin: sc.Variable = None,
                 vmax: sc.Variable = None,
                 aspect: Literal['auto', 'equal'] = 'auto',
                 scale: Dict[str, str] = None,
                 cbar: bool = False):

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
        """
        Convert the underlying Matplotlib figure to an image widget from ``ipywidgets``.
        """
        from ipywidgets import Image
        return Image(value=fig_to_bytes(self.fig), format='png')

    def autoscale(self, draw: bool = True):
        """
        Matplotlib's autoscale only takes lines into account. We require a special
        handling for meshes, which is part of the axes collections.

        Parameters
        ----------
        draw:
            Make a draw call to the figure if ``True``.
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
        """
        Make a draw call to the underlying figure.
        """
        self.fig.canvas.draw_idle()

    def savefig(self, filename: str, **kwargs):
        """
        Save plot to file.
        The default directory for writing the file is the same as the
        directory where the script or notebook is running.

        Parameters
        ----------
        filename:
            Save the figure to file. Possible file extensions are ``.jpg``, ``.png``
            and ``.pdf``.
        """
        self.fig.savefig(filename, **{**{'bbox_inches': 'tight'}, **kwargs})

    def show(self):
        """
        Make a call to Matplotlib's underlying ``show`` function.
        """
        self.fig.show()

    def crop(self, **limits):
        """
        Set the axes limits according to the crop parameters.

        Parameters
        ----------
        **limits:
            Min and max limits for each dimension to be cropped.
        """
        for xy, lims in limits.items():
            getattr(self.ax, f'set_{xy}lim')(*[
                sc.to_unit(number_to_variable(lims[m]), unit=lims['unit']).value
                for m in ('min', 'max') if m in lims
            ])

    def legend(self):
        """
        Add a legend to the figure.
        """
        self.ax.legend()

    @property
    def xlabel(self):
        return self.ax.get_xlabel()

    @xlabel.setter
    def xlabel(self, lab: str):
        self.ax.set_xlabel(lab)

    @property
    def ylabel(self):
        return self.ax.get_ylabel()

    @ylabel.setter
    def ylabel(self, lab: str):
        self.ax.set_ylabel(lab)

    @property
    def xscale(self):
        return self.ax.get_xscale()

    @xscale.setter
    def xscale(self, scale: Literal['linear', 'log']):
        self.ax.set_xscale(scale)

    @property
    def yscale(self):
        return self.ax.get_yscale()

    @yscale.setter
    def yscale(self, scale: Literal['linear', 'log']):
        self.ax.set_yscale(scale)

    def reset_mode(self):
        """
        Reset the Matplotlib toolbar mode to nothing, to disable all Zoom/Pan tools.
        """
        self.fig.canvas.toolbar.mode = ''

    def zoom(self):
        """
        Activate the underlying Matplotlib zoom tool.
        """
        self.fig.canvas.toolbar.zoom()

    def pan(self):
        """
        Activate the underlying Matplotlib pan tool.
        """
        self.fig.canvas.toolbar.pan()

    def save(self):
        """
        Save the figure to a PNG file via a pop-up dialog.
        """
        self.fig.canvas.toolbar.save_figure()

    def logx(self):
        """
        Toggle the scale between ``linear`` and ``log`` along the horizontal axis.
        """
        self.xscale = 'log' if self.xscale == 'linear' else 'linear'
        self._xmin = np.inf
        self._xmax = np.NINF
        self.autoscale()

    def logy(self):
        """
        Toggle the scale between ``linear`` and ``log`` along the vertical axis.
        """
        self.yscale = 'log' if self.yscale == 'linear' else 'linear'
        self._ymin = np.inf
        self._ymax = np.NINF
        self.autoscale()
