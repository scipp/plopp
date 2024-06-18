# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import uuid
from typing import Literal

import numpy as np
import scipp as sc
from matplotlib.dates import date2num
from matplotlib.lines import Line2D
from numpy.typing import ArrayLike

from ...core.utils import merge_masks
from ...graphics.bbox import BoundingBox, axis_bounds
from ..common import make_line_data
from .canvas import Canvas
from .utils import make_legend, parse_dicts_in_kwargs


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

        # self._make_line(
        #     data=make_line_data(data=self._data, dim=self._dim),
        #     artist_number=artist_number,
        #     **args,
        # )

        # def _make_line(
        #     self,
        #     data: dict,
        #     artist_number: int,
        #     errorbars: bool = True,
        #     mask_color: str = 'black',
        #     **kwargs,
        # ):
        #     """
        #     Create either plot markers or a step function, depending on whether the data
        #     contains bin edges or not.

        #     Parameters
        #     ----------
        #     data:
        #         A dictionary containing data entries that have been pre-processed to be in
        #         a format that Matplotlib can directly use.
        #     artist_number:
        #         The line artist_number to set colors and marker style.
        #     errorbars:
        #         Show errorbars if ``True``.
        #     mask_color:
        #         The color to be used to represent the masks.
        #     **kwargs:
        #         The kwargs are forwarded to:

        #         - ``matplotlib.pyplot.plot`` for data with a non bin-edge coordinate
        #         - ``matplotlib.pyplot.step`` for data with a bin-edge coordinate
        #     """
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
        # self._line._plopp_mask = line_mask

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
            # # Set the selection mask on the line collection that makes the segments
            # self._error[2][0]._plopp_mask = (
            #     line_mask[1:] if line_data["hist"] else line_mask
            # )

        if self.label and self._canvas._legend:
            self._ax.legend(**make_legend(self._canvas._legend))

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

        self._line.set_data(new_values['values']['x'], new_values['values']['y'])
        self._mask.set_data(new_values['mask']['x'], new_values['mask']['y'])
        self._mask.set_visible(new_values['mask']['visible'])

        if (self._error is not None) and (new_values['stddevs'] is not None):
            coll = self._error.get_children()[0]
            coll.set_segments(
                self._change_segments_y(
                    _to_float(new_values['stddevs']['x']),
                    _to_float(new_values['stddevs']['y']),
                    _to_float(new_values['stddevs']['e']),
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

    def bbox(self, xscale: Literal['linear', 'log'], yscale: Literal['linear', 'log']):
        """
        The bounding box of the line.
        """
        line_x = self._data.coords[self._dim]
        line_y = self._data.data
        if self._data.masks:
            line_y = line_y[merge_masks(self._data.masks)]
        if self._error is not None:
            stddevs = sc.stddevs(self._data)
            line_y = sc.concat([line_y - stddevs, line_y + stddevs], self._dim)

        return BoundingBox(
            **{**axis_bounds(('xmin', 'xmax'), line_x, xscale, pad=True)},
            **{**axis_bounds(('ymin', 'ymax'), line_y, yscale, pad=True)},
        )
