# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import uuid
from typing import Literal

import numpy as np
import plotly.graph_objects as go
import scipp as sc
from plotly.colors import qualitative as plotly_colors

from ...graphics.bbox import BoundingBox
from ..common import check_ndim, make_line_bbox, make_line_data
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
    uid:
        The unique identifier of the artist. If None, a random UUID is generated.
    artist_number:
        The canvas keeps track of how many lines have been added to it. This number is
        used to set the color and marker parameters of the line.
    errorbars:
        Show errorbars if ``True``.
    mask_color:
        The color to be used to represent the masks.
    mode:
        The mode of the line, either 'markers' or 'lines'.
    marker:
        The marker style to use.
    """

    def __init__(
        self,
        canvas: Canvas,
        data: sc.DataArray,
        uid: str | None = None,
        artist_number: int = 0,
        errorbars: bool = True,
        mask_color: str = 'black',
        mode: str | None = None,
        marker: str | None = None,
        **kwargs,
    ):
        check_ndim(data, ndim=1, origin='Line')
        self.uid = uid if uid is not None else uuid.uuid4().hex
        self._fig = canvas.fig
        self._data = data

        line_args = _parse_dicts_in_kwargs(kwargs, name=data.name)

        self._line = None
        self._mask = None
        self._error = None
        self._unit = None
        self.label = data.name
        self._dim = self._data.dim
        self._unit = self._data.unit
        self._coord = self._data.coords[self._dim]

        line_data = make_line_data(data=self._data, dim=self._dim)

        default_colors = plotly_colors.Plotly
        default_line_style = {
            'color': default_colors[artist_number % len(default_colors)]
        }
        default_marker_style = {
            'symbol': artist_number % 52  # Plotly has 52 marker styles
        }

        line_shape = None

        if mode is None:
            if line_data["hist"]:
                line_shape = 'vh'
                mode = 'lines'
            else:
                mode = 'markers'

        marker_style = default_marker_style if marker is None else marker
        line_style = {**default_line_style, **line_args}

        self._line = go.Scatter(
            x=np.asarray(line_data['values']['x']),
            y=np.asarray(line_data['values']['y']),
            name=self.label,
            mode=mode,
            marker=marker_style,
            line_shape=line_shape,
            line=line_style,
        )

        if errorbars and (line_data['stddevs'] is not None):
            self._error = go.Scatter(
                x=np.asarray(line_data['stddevs']['x']),
                y=np.asarray(line_data['stddevs']['y']),
                line=line_style,
                name=self.label,
                mode='markers',
                marker={'opacity': 0},
                error_y={'type': 'data', 'array': line_data['stddevs']['e']},
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
        if 'lines' in mode:
            line_style['color'] = mask_color

        self._mask = go.Scatter(
            x=np.asarray(line_data['mask']['x']),
            y=np.asarray(line_data['mask']['y']),
            name=self.label,
            mode=mode,
            marker=marker_style,
            line_shape=line_shape,
            line=line_style,
            visible=line_data['mask']['visible'],
            showlegend=False,
        )

        # Below, we need to re-define the line because it seems that the Scatter trace
        # that ends up in the figure is a copy of the one above.
        # Plotly has no concept of zorder, so we need to add the traces in a specific
        # order
        if 'lines' in mode:
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

        self._line._plopp_id = self.uid
        self._mask._plopp_id = self.uid
        if self._error is not None:
            self._error._plopp_id = self.uid

    def update(self, new_values: sc.DataArray):
        """
        Update the x and y positions of the data points from new data.

        Parameters
        ----------
        new_values:
            New data to update the line values, masks, errorbars from.
        """
        check_ndim(new_values, ndim=1, origin='Line')
        self._data = new_values
        line_data = make_line_data(data=self._data, dim=self._dim)

        with self._fig.batch_update():
            self._line.update(
                {'x': line_data['values']['x'], 'y': line_data['values']['y']}
            )

            if (self._error is not None) and (line_data['stddevs'] is not None):
                self._error.update(
                    {
                        'x': line_data['stddevs']['x'],
                        'y': line_data['stddevs']['y'],
                        'error_y': {'array': line_data['stddevs']['e']},
                    }
                )

            if line_data['mask']['visible']:
                update = {'x': line_data['mask']['x'], 'y': line_data['mask']['y']}
                self._mask.update(update)
                self._mask.visible = True
            else:
                self._mask.visible = False

    def remove(self):
        """
        Remove the line, masks and errorbar artists from the canvas.
        """
        self._fig.data = [
            trace for trace in list(self._fig.data) if trace._plopp_id != self.uid
        ]

    @property
    def color(self) -> str:
        """
        The line color.
        """
        return self._line.line.color

    @color.setter
    def color(self, val: str):
        self._line.line.color = val

    @property
    def style(self) -> str:
        """
        The line style.
        """
        return self._line.mode

    @style.setter
    def style(self, val: str):
        self._line.mode = val

    @property
    def width(self) -> float:
        """
        The line width.
        """
        return self._line.line.width

    @width.setter
    def width(self, val: float):
        self._line.line.width = val

    @property
    def marker(self) -> str:
        """
        The marker style.
        """
        return self._line.marker

    @marker.setter
    def marker(self, val: str):
        self._line.marker = val
        self._mask.marker = val

    @property
    def visible(self) -> bool:
        """
        The visibility of the line.
        """
        return self._line.visible

    @visible.setter
    def visible(self, val: bool):
        self._line.visible = val
        self._mask.visible = val
        if self._error is not None:
            self._error.visible = val

    @property
    def opacity(self) -> float:
        """
        The opacity of the line.
        """
        return self._line.opacity

    @opacity.setter
    def opacity(self, val: float):
        self._line.opacity = val
        self._mask.opacity = val
        if self._error is not None:
            self._error.opacity = val

    def bbox(
        self, xscale: Literal['linear', 'log'], yscale: Literal['linear', 'log']
    ) -> BoundingBox:
        """
        The bounding box of the line.
        This includes the x and y bounds of the line and optionally the error bars.

        Parameters
        ----------
        xscale:
            The scale of the x-axis.
        yscale:
            The scale of the y-axis.
        """
        out = make_line_bbox(
            data=self._data,
            dim=self._dim,
            errorbars=self._error is not None,
            xscale=xscale,
            yscale=yscale,
        )
        if xscale == 'log':
            out.xmin = np.log10(out.xmin)
            out.xmax = np.log10(out.xmax)
        if yscale == 'log':
            out.ymin = np.log10(out.ymin)
            out.ymax = np.log10(out.ymax)
        return out
