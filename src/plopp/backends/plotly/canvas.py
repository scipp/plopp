# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ...core.limits import find_limits, fix_empty_range
from ...core.utils import maybe_variable_to_number
# from .utils import fig_to_bytes, silent_mpl_figure

import plotly.graph_objects as go

import matplotlib.pyplot as plt
from matplotlib.collections import QuadMesh
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import scipp as sc
from typing import Dict, Literal, Tuple, Union


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

    def __init__(
            self,
            #  ax: plt.Axes = None,
            #  cax: plt.Axes = None,
            figsize: Tuple[float, float] = None,
            title: str = None,
            grid: bool = False,
            vmin: Union[sc.Variable, int, float] = None,
            vmax: Union[sc.Variable, int, float] = None,
            aspect: Literal['auto', 'equal'] = 'auto',
            scale: Dict[str, str] = None,
            cbar: bool = False,
            **ignored):

        self.fig = go.FigureWidget(
            layout={
                'modebar_remove': [
                    'zoom', 'pan', 'select', 'toImage', 'zoomIn', 'zoomOut',
                    'autoScale', 'resetScale', 'lasso2d'
                ],
                'margin': {
                    'l': 0,
                    'r': 0,
                    't': 0 if title is None else 40,
                    'b': 0
                },
                'dragmode':
                False,
                'width':
                600 if figsize is None else figsize[0],
                'height':
                400 if figsize is None else figsize[1]
            })
        # self.ax = ax
        # self.cax = cax
        self.figsize = figsize
        self._user_vmin = vmin
        self._user_vmax = vmax
        # self._scale = {} if scale is None else scale
        self.xunit = None
        self.yunit = None
        self._own_axes = False

        # if self.ax is None:
        #     self._own_axes = True
        #     with silent_mpl_figure():
        #         self.fig, self.ax = plt.subplots(figsize=figsize)
        #     if hasattr(self.fig.canvas, "on_widget_constructed"):
        #         self.fig.canvas.toolbar_visible = False
        #         self.fig.canvas.header_visible = False
        # else:
        #     self.fig = self.ax.get_figure()

        # if cbar and self.cax is None:
        #     divider = make_axes_locatable(self.ax)
        #     self.cax = divider.append_axes("right", "4%", pad="5%")

        # self.ax.set_aspect(aspect)
        # self.ax.set_title(title)
        # self.ax.grid(grid)
        if title:
            self.title = title

        # self._xmin = np.inf
        # self._xmax = np.NINF
        # self._ymin = np.inf
        # self._ymax = np.NINF

    def to_widget(self):
        return self.fig

    def autoscale(self):
        """
        Matplotlib's autoscale only takes lines into account. We require a special
        handling for meshes, which is part of the axes collections.

        Parameters
        ----------
        draw:
            Make a draw call to the figure if ``True``.
        """
        self.fig.update_layout(yaxis={'autorange': True}, xaxis={'autorange': True})
        ymin = None
        ymax = None
        if (self._user_vmin is not None) or (self._user_vmax is not None):
            if None in (self._user_vmin, self._user_vmax):
                raise ValueError('With the Plotly backend, you have to specify both '
                                 'vmin and vmax.')
            ymin = maybe_variable_to_number(self._user_vmin, unit=self.yunit)
            ymax = maybe_variable_to_number(self._user_vmax, unit=self.yunit)
            self.fig.update_layout(yaxis={'autorange': False},
                                   xaxis={'autorange': True})
            self.fig.update_yaxes(range=[ymin, ymax])
        else:
            self.fig.update_layout(yaxis={'autorange': True}, xaxis={'autorange': True})

    # def draw(self):
    #     """
    #     Make a draw call to the underlying figure.
    #     """
    #     return
    #     # self.fig.canvas.draw_idle()

    def savefig(self, filename: str):
        """
        Save the figure to file.
        The default directory for writing the file is the same as the
        directory where the script or notebook is running.

        Parameters
        ----------
        filename:
            Name of the output file. Possible file extensions are ``.jpg``, ``.png``,
            ``.svg``, ``.pdf``, and ``.html`.
        """
        ext = filename.split('.')[-1]
        if ext == 'html':
            self.fig.write_html(filename)
        else:
            self.fig.write_image(filename)

    def crop(self, **limits):
        """
        Set the axes limits according to the crop parameters.

        Parameters
        ----------
        **limits:
            Min and max limits for each dimension to be cropped.
        """
        for xy, lims in limits.items():
            getattr(self.fig, f'update_{xy}axes')(range=[
                maybe_variable_to_number(lims[m], unit=getattr(self, f'{xy}unit'))
                for m in ('min', 'max') if m in lims
            ])

    @property
    def title(self) -> str:
        return self.fig.layout.title

    @title.setter
    def title(self, title: str):
        layout = self.fig.layout
        if layout.margin.t == 0:
            layout.margin.t = 40
        layout.title = title

    @property
    def xlabel(self):
        return self.fig.layout.xaxis.title

    @xlabel.setter
    def xlabel(self, lab: str):
        self.fig.layout.xaxis.title = lab

    @property
    def ylabel(self):
        return self.fig.layout.yaxis.title

    @ylabel.setter
    def ylabel(self, lab: str):
        self.fig.layout.yaxis.title = lab

    @property
    def xscale(self):
        return self.fig.layout.xaxis.type

    @xscale.setter
    def xscale(self, scale: Literal['linear', 'log']):
        self.fig.update_xaxes(type=scale)

    @property
    def yscale(self):
        return self.fig.layout.yaxis.type

    @yscale.setter
    def yscale(self, scale: Literal['linear', 'log']):
        # self.ax.set_yscale(scale)
        self.fig.update_yaxes(type=scale)

    @property
    def xmin(self):
        return self.fig.layout.xaxis.range[0]

    @xmin.setter
    def xmin(self, value: float):
        self.fig.layout.xaxis.range = [value, self.xmax]

    @property
    def xmax(self):
        return self.fig.layout.xaxis.range[1]

    @xmax.setter
    def xmax(self, value: float):
        self.fig.layout.xaxis.range = [self.xmin, value]

    @property
    def xrange(self):
        return self.fig.layout.xaxis.range

    @xrange.setter
    def xrange(self, value: float):
        self.fig.layout.xaxis.range = value

    @property
    def ymin(self):
        return self.fig.layout.yaxis.range[0]

    @ymin.setter
    def ymin(self, value: float):
        self.fig.layout.yaxis.range = [value, self.ymax]

    @property
    def ymax(self):
        return self.fig.layout.yaxis.range[1]

    @ymax.setter
    def ymax(self, value: float):
        self.fig.layout.yaxis.range = [self.ymin, value]

    @property
    def yrange(self):
        return self.fig.layout.yaxis.range

    @yrange.setter
    def yrange(self, value: float):
        self.fig.layout.yaxis.range = value

    def reset_mode(self):
        """
        Reset the Matplotlib toolbar mode to nothing, to disable all Zoom/Pan tools.
        """
        self.fig.update_layout(dragmode=False)
        # if self.fig.canvas.toolbar.mode == 'zoom rect':
        #     self.zoom()
        # elif self.fig.canvas.toolbar.mode == 'pan/zoom':
        #     self.pan()

    def zoom(self):
        """
        Activate the underlying Matplotlib zoom tool.
        """
        self.fig.update_layout(dragmode='zoom')

    def pan(self):
        """
        Activate the underlying Matplotlib pan tool.
        """
        self.fig.update_layout(dragmode='pan')

    def save_figure(self):
        """
        Save the figure to a PNG file via a pop-up dialog.
        """
        self.fig.write_image('figure.png')

    def logx(self):
        """
        Toggle the scale between ``linear`` and ``log`` along the horizontal axis.
        """
        self.xscale = 'log' if self.xscale in ('linear', None) else 'linear'
        self.autoscale()

    def logy(self):
        """
        Toggle the scale between ``linear`` and ``log`` along the vertical axis.
        """
        self.yscale = 'log' if self.yscale in ('linear', None) else 'linear'
        self.autoscale()

    def finalize(self):
        """
        """
        return
