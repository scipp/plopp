# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ...core.limits import find_limits, fix_empty_range
from ...core.utils import maybe_variable_to_number
from .utils import fig_to_bytes, silent_mpl_figure

import matplotlib.pyplot as plt
from matplotlib.collections import QuadMesh
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import scipp as sc
from typing import Dict, Literal, Tuple, Union, Optional


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
    cax:
        If supplied, use these axes for the colorbar. If none are supplied, and a
        colorbar is required, the canvas will create its own axes.
    figsize:
        The width and height of the figure, in inches.
    title:
        The title to be placed above the figure.
    grid:
        Display the figure grid if ``True``.
    vmin:
        The minimum value for the vertical axis. If a number (without a unit) is
        supplied, it is assumed that the unit is the same as the current vertical axis
        unit.
    vmax:
        The maximum value for the vertical axis. If a number (without a unit) is
        supplied, it is assumed that the unit is the same as the current vertical axis
        unit.
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
                 cax: plt.Axes = None,
                 figsize: Optional[Tuple[float, float]] = None,
                 title: str = None,
                 grid: bool = False,
                 vmin: Union[sc.Variable, int, float] = None,
                 vmax: Union[sc.Variable, int, float] = None,
                 aspect: Literal['auto', 'equal'] = 'auto',
                 scale: Dict[str, str] = None,
                 cbar: bool = False,
                 **ignored):

        self.fig = None
        self.ax = ax
        self.cax = cax
        self._user_vmin = vmin
        self._user_vmax = vmax
        self._scale = {} if scale is None else scale
        self.xunit = None
        self.yunit = None
        self._own_axes = False

        if self.ax is None:
            self._own_axes = True
            with silent_mpl_figure():
                self.fig, self.ax = plt.subplots(
                    figsize=(6., 4.) if figsize is None else figsize)
            if self.is_widget():
                self.fig.canvas.toolbar_visible = False
                self.fig.canvas.header_visible = False
        else:
            self.fig = self.ax.get_figure()

        if cbar and self.cax is None:
            divider = make_axes_locatable(self.ax)
            self.cax = divider.append_axes("right", "4%", pad="5%")

        self.ax.set_aspect(aspect)
        self.ax.set_title(title)
        self.ax.grid(grid)

        self._xmin = np.inf
        self._xmax = np.NINF
        self._ymin = np.inf
        self._ymax = np.NINF

    def is_widget(self):
        return hasattr(self.fig.canvas, "on_widget_constructed")

    def to_image(self):
        """
        Convert the underlying Matplotlib figure to an image widget from ``ipywidgets``.
        """
        from ipywidgets import Image
        return Image(value=fig_to_bytes(self.fig), format='png')

    def to_widget(self):
        if self.is_widget():
            return self.fig.canvas
        else:
            return self.to_image()

    def autoscale(self):
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
        if self._user_vmin is not None:
            self._ymin = maybe_variable_to_number(self._user_vmin, unit=self.yunit)
        if self._user_vmax is not None:
            self._ymax = maybe_variable_to_number(self._user_vmax, unit=self.yunit)

        self.ax.set_xlim(_none_if_not_finite(self._xmin),
                         _none_if_not_finite(self._xmax))
        self.ax.set_ylim(_none_if_not_finite(self._ymin),
                         _none_if_not_finite(self._ymax))
        self.draw()

    def draw(self):
        """
        Make a draw call to the underlying figure.
        """
        self.fig.canvas.draw_idle()

    def savefig(self, filename: str, **kwargs):
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
                maybe_variable_to_number(lims[m], unit=getattr(self, f'{xy}unit'))
                for m in ('min', 'max') if m in lims
            ])

    # def legend(self):
    #     """
    #     Add a legend to the figure.
    #     """
    #     self.ax.legend()

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

    @property
    def xmin(self):
        return self.ax.get_xlim()[0]

    @xmin.setter
    def xmin(self, value: float):
        self.ax.set_xlim(value, self.xmax)

    @property
    def xmax(self):
        return self.ax.get_xlim()[1]

    @xmax.setter
    def xmax(self, value: float):
        self.ax.set_xlim(self.xmin, value)

    @property
    def xrange(self):
        return self.ax.get_xlim()

    @xrange.setter
    def xrange(self, value: float):
        self.ax.set_xlim(value)

    @property
    def ymin(self):
        return self.ax.get_ylim()[0]

    @ymin.setter
    def ymin(self, value: float):
        self.ax.set_ylim(value, self.ymax)

    @property
    def ymax(self):
        return self.ax.get_ylim()[1]

    @ymax.setter
    def ymax(self, value: float):
        self.ax.set_ylim(self.ymin, value)

    @property
    def yrange(self):
        return self.ax.get_ylim()

    @yrange.setter
    def yrange(self, value: float):
        self.ax.set_ylim(value)

    def reset_mode(self):
        """
        Reset the Matplotlib toolbar mode to nothing, to disable all Zoom/Pan tools.
        """
        if self.fig.canvas.toolbar.mode == 'zoom rect':
            self.zoom()
        elif self.fig.canvas.toolbar.mode == 'pan/zoom':
            self.pan()

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

    def save_figure(self):
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

    def finalize(self):
        """
        Trim the margins around the figure.
        """
        if self._own_axes:
            self.fig.tight_layout()
