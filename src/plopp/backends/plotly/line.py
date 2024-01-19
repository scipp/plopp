# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import uuid
from typing import Any, Dict, Literal

import numpy as np
import scipp as sc

from ..common import make_line_data
from .canvas import Canvas


def _parse_dicts_in_kwargs(kwargs, name):
    out = {}
    for key, value in kwargs.items():
        if isinstance(value, dict):
            if name in value:
                out[key] = value[name]
        else:
            out[key] = value
    return out


def _make_graph_object(
    x: np.ndarray, y: np.ndarray, projection: Literal['default', 'polar'], **kwargs
):
    from plotly.graph_objects import Scatter, Scatterpolar

    if projection == 'default':
        return Scatter(x=x, y=y, **kwargs)
    elif projection == 'polar':
        return Scatterpolar(r=y, theta=x, **kwargs)


class Line:
    """
    Artist to represent one-dimensional data.
    If the coordinate is bin centers, the line is (by default) a set of markers.
    If the coordinate is bin edges, the line is a step function.

    Parameters
    ----------
    canvas:
        The canvas that will display the line.
    data:
        The initial data to create the line from.
    number:
        The canvas keeps track of how many lines have been added to it. This number is
        used to set the color and marker parameters of the line.
    projection:
        The axes projection. If ``None``, the normal go.Scatter is used to draw the
        line. If ``polar``, the go.Scatterpolar is used to draw the line.
    """

    def __init__(
        self,
        canvas: Canvas,
        data: sc.DataArray,
        number: int = 0,
        projection: Literal['default', 'polar'] = 'default',
        **kwargs,
    ):
        self._fig = canvas.fig
        self._data = data

        args = _parse_dicts_in_kwargs(kwargs, name=data.name)

        self._line = None
        self._mask = None
        self._error = None
        self._unit = None
        self.label = data.name
        self._dim = self._data.dim
        self._unit = self._data.unit
        self._coord = self._data.coords[self._dim]
        self._id = uuid.uuid4().hex

        self._make_line(
            data=make_line_data(data=self._data, dim=self._dim),
            number=number,
            projection=projection,
            **args,
        )

    def _make_line(
        self,
        data: Dict,
        number: int,
        projection: Literal['default', 'polar'],
        errorbars: bool = True,
        mask_color: str = 'black',
        mode='markers',
        marker=None,
        **kwargs,
    ):
        """
        Create either plot markers or a step function, depending on whether the data
        contains bin edges or not.

        Parameters
        ----------
        data:
            A dictionary containing data entries that have been pre-processed to be in
            a format that Matplotlib can directly use.
        number:
            The line number to set colors and marker style.
        errorbars:
            Show errorbars if ``True``.
        mask_color:
            The color to be used to represent the masks.
        **kwargs:
            The kwargs are forwarded to:

            - ``matplotlib.pyplot.plot`` for data with a non bin-edge coordinate
            - ``matplotlib.pyplot.step`` for data with a bin-edge coordinate
        """
        from plotly.colors import qualitative as plotly_colors

        default_colors = plotly_colors.Plotly
        default_line_style = {'color': default_colors[number % len(default_colors)]}
        default_marker_style = {'symbol': number % 53}  # Plotly has 52 marker styles

        line_shape = None

        if data["hist"]:
            line_shape = 'vh'
            mode = 'lines'

        marker_style = default_marker_style if marker is None else marker
        line_style = {**default_line_style, **kwargs}

        self._line = _make_graph_object(
            x=np.asarray(data['values']['x']),
            y=np.asarray(data['values']['y']),
            projection=projection,
            name=self.label,
            mode=mode,
            marker=marker_style,
            line_shape=line_shape,
            line=line_style,
        )

        if errorbars and (data['stddevs'] is not None):
            self._error = _make_graph_object(
                x=np.asarray(data['stddevs']['x']),
                y=np.asarray(data['stddevs']['y']),
                projection=projection,
                line=line_style,
                name=self.label,
                mode='markers',
                marker={'opacity': 0},
                error_y={'type': 'data', 'array': data['stddevs']['e']},
                showlegend=False,
            )

        marker_line_style = {'width': 3, 'color': mask_color}
        if 'line' in marker_style:
            marker_style['line'].update(marker_line_style)
        else:
            marker_style['line'] = marker_line_style
        if 'width' in line_style:
            line_style['width'] *= 5
        else:
            line_style['width'] = 5
        if data["hist"]:
            line_style['color'] = mask_color

        self._mask = _make_graph_object(
            x=np.asarray(data['mask']['x']),
            y=np.asarray(data['mask']['y']),
            projection=projection,
            name=self.label,
            mode=mode,
            marker=marker_style,
            line_shape=line_shape,
            line=line_style,
            visible=data['mask']['visible'],
            showlegend=False,
        )

        # Below, we need to re-define the line because it seems that the Scatter trace
        # that ends up in the figure is a copy of the one above.
        # Plotly has no concept of zorder, so we need to add the traces in a specific
        # order
        if data["hist"]:
            self._fig.add_trace(self._mask)
            self._mask = self._fig.data[-1]
            self._fig.add_trace(self._line)
            self._line = self._fig.data[-1]
            if self._error is not None:
                self._fig.add_trace(self._error)
                self._error = self._fig.data[-1]
        else:
            self._fig.add_trace(self._line)
            self._line = self._fig.data[-1]
            if self._error is not None:
                self._fig.add_trace(self._error)
                self._error = self._fig.data[-1]
            self._fig.add_trace(self._mask)
            self._mask = self._fig.data[-1]
        self._line._plopp_id = self._id
        line_mask = ~np.isnan(data['mask']['y'])
        self._line._plopp_mask = line_mask
        self._mask._plopp_id = self._id
        if self._error is not None:
            self._error._plopp_id = self._id
            self._error._plopp_mask = line_mask[1:] if data["hist"] else line_mask

    def update(self, new_values: sc.DataArray):
        """
        Update the x and y positions of the data points from new data.

        Parameters
        ----------
        new_values:
            New data to update the line values, masks, errorbars from.
        """
        self._data = new_values
        new_values = make_line_data(data=self._data, dim=self._dim)

        with self._fig.batch_update():
            self._line.update(
                {'x': new_values['values']['x'], 'y': new_values['values']['y']}
            )

            if (self._error is not None) and (new_values['stddevs'] is not None):
                self._error.update(
                    {
                        'x': new_values['stddevs']['x'],
                        'y': new_values['stddevs']['y'],
                        'error_y': {'array': new_values['stddevs']['e']},
                    }
                )

            if new_values['mask']['visible']:
                update = {'x': new_values['mask']['x'], 'y': new_values['mask']['y']}
                self._mask.update(update)
                self._mask.visible = True
            else:
                self._mask.visible = False

    def remove(self):
        """
        Remove the line, masks and errorbar artists from the canvas.
        """
        self._fig.data = [
            trace for trace in list(self._fig.data) if trace._plopp_id != self._id
        ]

    @property
    def color(self):
        """
        The line color.
        """
        return self._line.line.color

    @color.setter
    def color(self, val):
        self._line.line.color = val
