# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import uuid
from typing import Literal

import numpy as np
import scipp as sc
from matplotlib.dates import date2num
from matplotlib.lines import Line2D
from numpy.typing import ArrayLike

from ...graphics.bbox import BoundingBox
from ..common import check_ndim, make_line_bbox, make_line_data
from .canvas import Canvas
from .utils import parse_dicts_in_kwargs


def _to_float(x):
    return date2num(x) if np.issubdtype(x.dtype, np.datetime64) else x


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
    artist_number:
        The canvas keeps track of how many lines have been added to it. This number is
        used to set the color and marker parameters of the line.
    """

    def __init__(
        self,
        canvas: Canvas,
        data: sc.DataArray,
        artist_number: int = 0,
        errorbars: bool = True,
        mask_color: str = 'black',
        **kwargs,
    ):
        check_ndim(data, ndim=1, origin='Line')
        self._canvas = canvas
        self._ax = self._canvas.ax
        self._data = data
        # Because all keyword arguments from the figure are forwarded to both the canvas
        # and the line, we need to remove the arguments that belong to the canvas.
        kwargs.pop('ax', None)

        line_args = parse_dicts_in_kwargs(kwargs, name=data.name)

        self._line = None
        self._mask = None
        self._error = None
        self._unit = None
        self.label = data.name
        self._dim = self._data.dim
        self._unit = self._data.unit
        self._coord = self._data.coords[self._dim]
        self._id = uuid.uuid4().hex

        aliases = {'ls': 'linestyle', 'lw': 'linewidth', 'c': 'color'}
        for key, alias in aliases.items():
            if key in line_args:
                line_args[alias] = line_args.pop(key)

        line_data = make_line_data(data=self._data, dim=self._dim)

        default_step_style = {
            'linestyle': 'solid',
            'linewidth': 1.5,
            'color': f'C{artist_number}',
        }
        markers = list(Line2D.markers.keys())
        default_plot_style = {
            'linestyle': 'none',
            'linewidth': 1.5,
            'marker': markers[(artist_number + 2) % len(markers)],
            'color': f'C{artist_number}',
        }

        if line_data["hist"]:
            self._line = self._ax.step(
                line_data['values']['x'],
                line_data['values']['y'],
                label=self.label,
                zorder=10,
                **{**default_step_style, **line_args},
            )[0]

            self._mask = self._ax.step(line_data['mask']['x'], line_data['mask']['y'])[
                0
            ]
            self._mask.update_from(self._line)
            self._mask.set_color(mask_color)
            self._mask.set_label(None)
            self._mask.set_linewidth(self._mask.get_linewidth() * 3)
            self._mask.set_zorder(self._mask.get_zorder() - 1)
            self._mask.set_visible(line_data['mask']['visible'])
        else:
            self._line = self._ax.plot(
                line_data['values']['x'],
                line_data['values']['y'],
                label=self.label,
                zorder=10,
                **{**default_plot_style, **line_args},
            )[0]
            self._mask = self._ax.plot(
                line_data['mask']['x'],
                line_data['mask']['y'],
                zorder=11,
                mec=mask_color,
                mfc="None",
                mew=3.0,
                linestyle="none",
                marker=self._line.get_marker(),
                visible=line_data['mask']['visible'],
            )[0]

        self.line_mask = sc.array(dims=['x'], values=~np.isnan(line_data['mask']['y']))

        # Add error bars
        if errorbars and (line_data['stddevs'] is not None):
            self._error = self._ax.errorbar(
                line_data['stddevs']['x'],
                line_data['stddevs']['y'],
                yerr=line_data['stddevs']['e'],
                color=self._line.get_color(),
                zorder=10,
                fmt="none",
            )

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
        self.line_mask = sc.array(dims=['x'], values=~np.isnan(line_data['mask']['y']))

        self._line.set_data(line_data['values']['x'], line_data['values']['y'])
        self._mask.set_data(line_data['mask']['x'], line_data['mask']['y'])
        self._mask.set_visible(line_data['mask']['visible'])

        if (self._error is not None) and (line_data['stddevs'] is not None):
            coll = self._error.get_children()[0]
            coll.set_segments(
                self._change_segments_y(
                    _to_float(line_data['stddevs']['x']),
                    _to_float(line_data['stddevs']['y']),
                    _to_float(line_data['stddevs']['e']),
                )
            )

    def _change_segments_y(self, x: ArrayLike, y: ArrayLike, e: ArrayLike) -> ArrayLike:
        """
        Update the positions of the errorbars when `update_data` is called.
        """
        arr1 = np.repeat(x, 2)
        arr2 = np.array([y - e, y + e]).T.flatten()
        return np.array([arr1, arr2]).T.flatten().reshape(len(y), 2, 2)

    def remove(self):
        """
        Remove the line, masks and errorbar artists from the canvas.
        """
        self._line.remove()
        self._mask.remove()
        if self._error is not None:
            self._error.remove()
        self._canvas.draw()

    @property
    def color(self):
        """
        The line color.
        """
        return self._line.get_color()

    @color.setter
    def color(self, val):
        self._line.set_color(val)
        if self._error is not None:
            for artist in self._error.get_children():
                artist.set_color(val)
        self._canvas.draw()

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
        return make_line_bbox(
            data=self._data,
            dim=self._dim,
            errorbars=self._error is not None,
            xscale=xscale,
            yscale=yscale,
        )
