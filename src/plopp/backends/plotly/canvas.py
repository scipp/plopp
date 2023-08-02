# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from typing import Literal, Tuple, Union

import scipp as sc

from ...core.utils import maybe_variable_to_number


class Canvas:
    """
    Plotly-based canvas used to render 2D graphics.
    It provides a figure and some axes, as well as functions for controlling the zoom,
    panning, and the scale of the axes.

    Parameters
    ----------
    figsize:
        The width and height of the figure, in inches.
    title:
        The title to be placed above the figure.
    vmin:
        The minimum value for the vertical axis. If a number (without a unit) is
        supplied, it is assumed that the unit is the same as the current vertical axis
        unit.
    vmax:
        The maximum value for the vertical axis. If a number (without a unit) is
        supplied, it is assumed that the unit is the same as the current vertical axis
        unit.
    cbar:
        Add axes to host a colorbar if ``True``.
    """

    def __init__(
        self,
        figsize: Tuple[float, float] = None,
        title: str = None,
        vmin: Union[sc.Variable, int, float] = None,
        vmax: Union[sc.Variable, int, float] = None,
        cbar: bool = False,
        **ignored,
    ):
        # Note on the `**ignored`` keyword arguments: the figure which owns the canvas
        # creates both the canvas and an artist object (Line or Image). The figure
        # accepts keyword arguments, and has to somehow forward them to the canvas and
        # the artist. Since the figure has no detailed knowledge of the underlying
        # backend that implements the canvas, it cannot have specific arguments (such
        # as `layout` for specifying a Plotly layout).
        # Instead, we forward all the kwargs from the figure to both the canvas and the
        # artist, and filter out the artist kwargs with `**ignored`.

        import plotly.graph_objects as go

        self.fig = go.FigureWidget(
            layout={
                'modebar_remove': [
                    'zoom',
                    'pan',
                    'select',
                    'toImage',
                    'zoomIn',
                    'zoomOut',
                    'autoScale',
                    'resetScale',
                    'lasso2d',
                ],
                'margin': {'l': 0, 'r': 0, 't': 0 if title is None else 40, 'b': 0},
                'dragmode': False,
                'width': 600 if figsize is None else figsize[0],
                'height': 400 if figsize is None else figsize[1],
            }
        )
        self.figsize = figsize
        self._user_vmin = vmin
        self._user_vmax = vmax
        self.units = {}
        self.dims = {}
        self._own_axes = False
        if title:
            self.title = title

    def to_widget(self):
        return self.fig

    def autoscale(self):
        """
        Auto-scale the axes ranges to show all data in the canvas.
        """
        ymin = None
        ymax = None
        if (self._user_vmin is not None) or (self._user_vmax is not None):
            if None in (self._user_vmin, self._user_vmax):
                raise ValueError(
                    'With the Plotly backend, you have to specify both '
                    'vmin and vmax.'
                )
            ymin = maybe_variable_to_number(self._user_vmin, unit=self.yunit)
            ymax = maybe_variable_to_number(self._user_vmax, unit=self.yunit)
            self.fig.update_layout(
                yaxis={'autorange': False}, xaxis={'autorange': True}
            )
            self.fig.update_yaxes(range=[ymin, ymax])
        else:
            self.fig.update_layout(yaxis={'autorange': True}, xaxis={'autorange': True})

    def save(self, filename: str):
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

    def set_axes(self, dims, units):
        """
        Set the axes dimensions and units.

        Parameters
        ----------
        dims:
            The dimensions of the data.
        units:
            The units of the data.
        """
        self.units = units
        self.dims = dims

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
        return self.fig.layout.title.text

    @title.setter
    def title(self, text: str):
        layout = self.fig.layout
        if not text:
            layout.margin.t = 0
        elif layout.margin.t == 0:
            layout.margin.t = 40
        layout.title = text

    @property
    def xlabel(self) -> str:
        """
        Get or set the label of the x-axis.
        """
        return self.fig.layout.xaxis.title.text

    @xlabel.setter
    def xlabel(self, lab: str):
        self.fig.layout.xaxis.title = lab

    @property
    def ylabel(self) -> str:
        """
        Get or set the label of the y-axis.
        """
        return self.fig.layout.yaxis.title.text

    @ylabel.setter
    def ylabel(self, lab: str):
        self.fig.layout.yaxis.title = lab

    @property
    def xscale(self) -> str:
        """
        Get or set the scale of the x-axis ('linear' or 'log').
        """
        return self.fig.layout.xaxis.type

    @xscale.setter
    def xscale(self, scale: Literal['linear', 'log']):
        self.fig.update_xaxes(type=scale)

    @property
    def yscale(self) -> str:
        """
        Get or set the scale of the y-axis ('linear' or 'log').
        """
        return self.fig.layout.yaxis.type

    @yscale.setter
    def yscale(self, scale: Literal['linear', 'log']):
        self.fig.update_yaxes(type=scale)

    @property
    def xmin(self) -> float:
        """
        Get or set the lower (left) bound of the x-axis.
        """
        return self.fig.layout.xaxis.range[0]

    @xmin.setter
    def xmin(self, value: float):
        self.fig.layout.xaxis.range = [value, self.xmax]

    @property
    def xmax(self) -> float:
        """
        Get or set the upper (right) bound of the x-axis.
        """
        return self.fig.layout.xaxis.range[1]

    @xmax.setter
    def xmax(self, value: float):
        self.fig.layout.xaxis.range = [self.xmin, value]

    @property
    def xrange(self) -> Tuple[float, float]:
        """
        Get or set the range/limits of the x-axis.
        """
        return self.fig.layout.xaxis.range

    @xrange.setter
    def xrange(self, value: Tuple[float, float]):
        self.fig.layout.xaxis.range = value

    @property
    def ymin(self) -> float:
        """
        Get or set the lower (bottom) bound of the y-axis.
        """
        return self.fig.layout.yaxis.range[0]

    @ymin.setter
    def ymin(self, value: float):
        self.fig.layout.yaxis.range = [value, self.ymax]

    @property
    def ymax(self) -> float:
        """
        Get or set the upper (top) bound of the y-axis.
        """
        return self.fig.layout.yaxis.range[1]

    @ymax.setter
    def ymax(self, value: float):
        self.fig.layout.yaxis.range = [self.ymin, value]

    @property
    def yrange(self) -> Tuple[float, float]:
        """
        Get or set the range/limits of the y-axis.
        """
        return self.fig.layout.yaxis.range

    @yrange.setter
    def yrange(self, value: Tuple[float, float]):
        self.fig.layout.yaxis.range = value

    def reset_mode(self):
        """
        Reset the modebar mode to nothing, to disable all zoom/pan tools.
        """
        self.fig.update_layout(dragmode=False)

    def zoom(self):
        """
        Activate the underlying Plotly zoom tool.
        """
        self.fig.update_layout(dragmode='zoom')

    def pan(self):
        """
        Activate the underlying Plotly pan tool.
        """
        self.fig.update_layout(dragmode='pan')

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
        self.fig.write_image('figure.png')

    def logx(self):
        """
        Toggle the scale between ``linear`` and ``log`` along the horizontal axis.
        """
        self.xscale = 'log' if self.xscale in ('linear', None) else 'linear'

    def logy(self):
        """
        Toggle the scale between ``linear`` and ``log`` along the vertical axis.
        """
        self.yscale = 'log' if self.yscale in ('linear', None) else 'linear'

    def finalize(self):
        """
        Finalize is called at the end of figure creation. Add any polishing operations
        here.
        """
        return
