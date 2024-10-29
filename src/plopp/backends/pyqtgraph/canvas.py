# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import warnings
from typing import Literal

import matplotlib.pyplot as plt
import numpy as np
import scipp as sc
from matplotlib import dates as mdates
from mpl_toolkits.axes_grid1 import make_axes_locatable

from ...core.utils import maybe_variable_to_number, scalar_to_string
from ...graphics.bbox import BoundingBox
from .utils import fig_to_bytes, is_sphinx_build, make_figure, make_legend


def _cursor_value_to_variable(x: float, dtype: sc.DType, unit: str) -> sc.Variable:
    if dtype == sc.DType.datetime64:
        # Annoying chain of conversion but matplotlib has its own way of converting
        # dates to numbers (number of days since epoch), and num2date returns a python
        # datetime object, while scipp expects a numpy datetime64.
        return sc.scalar(np.datetime64(mdates.num2date(x).replace(tzinfo=None))).to(
            unit=unit
        )
    return sc.scalar(x, unit=unit)


def _cursor_formatter(x: float, dtype: sc.DType, unit: str) -> str:
    if dtype == sc.DType.datetime64:
        return mdates.num2date(x).replace(tzinfo=None).isoformat()
    return scalar_to_string(sc.scalar(x, unit=unit))


def _maybe_trim_polar_limits(
    axis_type: str, limits: tuple[float, float]
) -> tuple[float, float]:
    """
    If the axes are polar, trim the limits of the polar plot to be within the range
    [0, 2π].

    Parameters
    ----------
    axis_type:
        The type of the axis. If this is not 'polar', the limits are returned as is.
    limits:
        The limits of the axis.
    """
    if axis_type != 'polar':
        return limits
    return tuple(np.clip(limits, 0, 2 * np.pi))


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
    user_vmin:
        The minimum value for the y axis (1d plots only).
    user_vmax:
        The maximum value for the y axis (1d plots only).
    aspect:
        The aspect ratio for the axes.
    cbar:
        Add axes to host a colorbar if ``True``.
    legend:
        Show legend if ``True``. If ``legend`` is a tuple, it should contain the
        ``(x, y)`` coordinates of the legend's anchor point in axes coordinates.
    """

    def __init__(
        self,
        ax: plt.Axes = None,
        cax: plt.Axes = None,
        figsize: tuple[float, float] | None = None,
        title: str | None = None,
        grid: bool = False,
        user_vmin: sc.Variable | float = None,
        user_vmax: sc.Variable | float = None,
        aspect: Literal['auto', 'equal', None] = None,
        cbar: bool = False,
        legend: bool | tuple[float, float] = True,
        **ignored,
    ):
        # Note on the `**ignored`` keyword arguments: the figure which owns the canvas
        # creates both the canvas and an artist object (Line or Image). The figure
        # accepts keyword arguments, and has to somehow forward them to the canvas and
        # the artist. Since the figure has no detailed knowledge of the underlying
        # backend that implements the canvas, it cannot have specific arguments (such
        # as `ax` for specifying Matplotlib axes).
        # Instead, we forward all the kwargs from the figure to both the canvas and the
        # artist, and filter out the artist kwargs with `**ignored`.

        self.fig = None
        self.ax = ax
        self.cax = cax
        self.bbox = BoundingBox()
        self._user_vmin = user_vmin
        self._user_vmax = user_vmax
        self.units = {}
        self.dims = {}
        self._legend = legend

        if self.ax is None:
            self.fig = make_figure(figsize=(6.0, 4.0) if figsize is None else figsize)
            self.ax = self.fig.add_subplot()
            if self.is_widget():
                self.fig.canvas.toolbar_visible = False
                self.fig.canvas.header_visible = False
        else:
            self.fig = self.ax.get_figure()
        if aspect is not None:
            self.ax.set_aspect(aspect)

        if cbar and (self.cax is None):
            if self.ax.name == 'polar':
                bounds = self.ax.get_position().bounds
                self.cax = self.fig.add_axes(
                    [bounds[0] + bounds[2] + 0.1, 0.1, 0.03, 0.8]
                )
            else:
                divider = make_axes_locatable(self.ax)
                self.cax = divider.append_axes("right", "4%", pad="5%")

        self.ax.grid(grid)
        if title:
            self.ax.set_title(title)
        self._coord_formatters = []

    def is_widget(self):
        return hasattr(self.fig.canvas, "on_widget_constructed")

    def to_image(self):
        """
        Convert the underlying Matplotlib figure to an image widget from ``ipywidgets``.
        """
        from ipywidgets import Image

        return Image(value=fig_to_bytes(self.fig), format='png')

    def to_widget(self):
        from ipywidgets import VBox

        if self.is_widget() and not is_sphinx_build():
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    self.fig.tight_layout()
            except RuntimeError:
                pass
            # The Matplotlib canvas tries to fill the entire width of the output cell,
            # which can add unnecessary whitespace between it and other widgets. To
            # prevent this, we wrap the canvas in a VBox, which seems to help.
            return VBox([self.fig.canvas])
        return self.to_image()

    def draw(self):
        """
        Make a draw call to the underlying figure.
        """
        self.fig.canvas.draw_idle()

    def update_legend(self):
        """
        Update the legend on the canvas.
        """
        if self._legend:
            handles, labels = self.ax.get_legend_handles_labels()
            if len(handles) > 1:
                self.ax.legend(handles, labels, **make_legend(self._legend))
            elif (leg := self.ax.get_legend()) is not None:
                leg.remove()

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

    def set_axes(self, dims, units, dtypes):
        """
        Set the axes dimensions and units.

        Parameters
        ----------
        dims:
            The dimensions of the data.
        units:
            The units of the data.
        dtypes:
            The data types of the data.
        """
        self.units = units
        self.dims = dims
        self.dtypes = dtypes
        self._cursor_x_prefix = ''
        self._cursor_y_prefix = ''
        if 'y' in self.dims:
            self._cursor_x_prefix = self.dims['x'] + '='
            self._cursor_y_prefix = self.dims['y'] + '='
        self.ax.format_coord = self.format_coord
        key = 'y' if 'y' in self.units else 'data'
        self.bbox = BoundingBox(
            ymin=maybe_variable_to_number(self._user_vmin, unit=self.units[key]),
            ymax=maybe_variable_to_number(self._user_vmax, unit=self.units[key]),
        )

    def register_format_coord(self, formatter):
        """
        Register a custom axis formatter for the x-axis.
        """
        self._coord_formatters.append(formatter)

    def format_coord(self, x: float, y: float) -> str:
        """
        Format the coordinates of the mouse pointer to show the value of the
        data at that point.

        Parameters
        ----------
        x:
            The x coordinate of the mouse pointer.
        y:
            The y coordinate of the mouse pointer.
        """
        xstr = _cursor_formatter(x, self.dtypes['x'], self.units['x'])
        key = 'y' if 'y' in self.dtypes else 'data'
        ystr = _cursor_formatter(y, self.dtypes[key], self.units[key])
        out = f"({self._cursor_x_prefix}{xstr}, {self._cursor_y_prefix}{ystr})"
        if not self._coord_formatters:
            return out
        xpos = (
            self.dims['x'],
            _cursor_value_to_variable(x, self.dtypes['x'], self.units['x']),
        )
        ypos = (
            (
                self.dims['y'],
                _cursor_value_to_variable(y, self.dtypes['y'], self.units['y']),
            )
            if 'y' in self.dims
            else None
        )
        extra = [formatter(xpos, ypos) for formatter in self._coord_formatters]
        extra = [e for e in extra if e is not None]
        if extra:
            out += ": {" + ", ".join(extra) + "}"
        return out

    @property
    def empty(self) -> bool:
        """
        Check if the canvas is empty.
        """
        return not self.dims

    @property
    def title(self) -> str:
        """
        Get or set the title of the plot.
        """
        return self.ax.get_title()

    @title.setter
    def title(self, text: str):
        self.ax.set_title(text)

    @property
    def xlabel(self) -> str:
        """
        Get or set the label of the x-axis.
        """
        return self.ax.get_xlabel()

    @xlabel.setter
    def xlabel(self, lab: str):
        self.ax.set_xlabel(lab)

    @property
    def ylabel(self) -> str:
        """
        Get or set the label of the y-axis.
        """
        return self.ax.get_ylabel()

    @ylabel.setter
    def ylabel(self, lab: str):
        self.ax.set_ylabel(lab)

    @property
    def cblabel(self) -> str:
        """
        Get or set the label of the colorbar.
        """
        return self.cax.get_ylabel()

    @cblabel.setter
    def cblabel(self, lab: str):
        self.cax.set_ylabel(lab)

    @property
    def xscale(self) -> Literal['linear', 'log']:
        """
        Get or set the scale of the x-axis ('linear' or 'log').
        """
        return self.ax.get_xscale()

    @xscale.setter
    def xscale(self, scale: Literal['linear', 'log']):
        self.ax.set_xscale(scale)

    @property
    def yscale(self) -> Literal['linear', 'log']:
        """
        Get or set the scale of the y-axis ('linear' or 'log').
        """
        return self.ax.get_yscale()

    @yscale.setter
    def yscale(self, scale: Literal['linear', 'log']):
        self.ax.set_yscale(scale)

    @property
    def xmin(self) -> float:
        """
        Get or set the lower (left) bound of the x-axis.
        """
        return self.ax.get_xlim()[0]

    @xmin.setter
    def xmin(self, value: float):
        self.ax.set_xlim(
            _maybe_trim_polar_limits(axis_type=self.ax.name, limits=(value, self.xmax))
        )

    @property
    def xmax(self) -> float:
        """
        Get or set the upper (right) bound of the x-axis.
        """
        return self.ax.get_xlim()[1]

    @xmax.setter
    def xmax(self, value: float):
        self.ax.set_xlim(
            _maybe_trim_polar_limits(axis_type=self.ax.name, limits=(self.xmin, value))
        )

    @property
    def xrange(self) -> tuple[float, float]:
        """
        Get or set the range/limits of the x-axis.
        """
        return self.ax.get_xlim()

    @xrange.setter
    def xrange(self, value: tuple[float, float]):
        self.ax.set_xlim(_maybe_trim_polar_limits(axis_type=self.ax.name, limits=value))

    @property
    def ymin(self) -> float:
        """
        Get or set the lower (bottom) bound of the y-axis.
        """
        return self.ax.get_ylim()[0]

    @ymin.setter
    def ymin(self, value: float):
        self.ax.set_ylim(value, self.ymax)

    @property
    def ymax(self) -> float:
        """
        Get or set the upper (top) bound of the y-axis.
        """
        return self.ax.get_ylim()[1]

    @ymax.setter
    def ymax(self, value: float):
        self.ax.set_ylim(self.ymin, value)

    @property
    def yrange(self) -> tuple[float, float]:
        """
        Get or set the range/limits of the y-axis.
        """
        return self.ax.get_ylim()

    @yrange.setter
    def yrange(self, value: tuple[float, float]):
        self.ax.set_ylim(value)

    @property
    def grid(self) -> bool:
        """
        Get or set the visibility of the grid.
        """
        return self.ax.axes.get_xgridlines()[0].get_visible()

    @grid.setter
    def grid(self, visible: bool):
        self.ax.grid(visible)

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

    def panzoom(self, value: Literal['pan', 'zoom', None]):
        """
        Activate or deactivate the pan or zoom tool, depending on the input value.
        """
        if value == 'zoom':
            self.zoom()
        elif value == 'pan':
            self.pan()
        elif value is None:
            self.reset_mode()

    def download_figure(self):
        """
        Save the figure to a PNG file via a pop-up dialog.
        """
        self.fig.canvas.toolbar.save_figure()

    def logx(self):
        """
        Toggle the scale between ``linear`` and ``log`` along the horizontal axis.
        """
        self.xscale = 'log' if self.xscale == 'linear' else 'linear'

    def logy(self):
        """
        Toggle the scale between ``linear`` and ``log`` along the vertical axis.
        """
        self.yscale = 'log' if self.yscale == 'linear' else 'linear'
