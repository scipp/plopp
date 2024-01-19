# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import uuid
from typing import Dict

import numpy as np
import scipp as sc
from matplotlib.lines import Line2D
from numpy.typing import ArrayLike

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
    """

    def __init__(self, canvas: Canvas, data: sc.DataArray, number: int = 0, **kwargs):
        self._canvas = canvas
        self._ax = self._canvas.ax
        self._data = data
        # Because all keyword arguments from the figure are forwarded to both the canvas
        # and the line, we need to remove the arguments that belong to the canvas.
        kwargs.pop('ax', None)

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

        aliases = {'ls': 'linestyle', 'lw': 'linewidth', 'c': 'color'}
        for key, alias in aliases.items():
            if key in args:
                args[alias] = args.pop(key)

        self._make_line(
            data=make_line_data(data=self._data, dim=self._dim),
            number=number,
            **args,
        )

    def _make_line(
        self,
        data: Dict,
        number: int,
        errorbars: bool = True,
        mask_color: str = 'black',
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

        default_step_style = {
            'linestyle': 'solid',
            'linewidth': 1.5,
            'color': f'C{number}',
        }
        markers = list(Line2D.markers.keys())
        default_plot_style = {
            'linestyle': 'none',
            'linewidth': 1.5,
            'marker': markers[(number + 2) % len(markers)],
            'color': f'C{number}',
        }

        if data["hist"]:
            self._line = self._ax.step(
                data['values']['x'],
                data['values']['y'],
                label=self.label,
                zorder=10,
                **{**default_step_style, **kwargs},
            )[0]

            self._mask = self._ax.step(data['mask']['x'], data['mask']['y'])[0]
            self._mask.update_from(self._line)
            self._mask.set_color(mask_color)
            self._mask.set_label(None)
            self._mask.set_linewidth(self._mask.get_linewidth() * 3)
            self._mask.set_zorder(self._mask.get_zorder() - 1)
            self._mask.set_visible(data['mask']['visible'])
        else:
            self._line = self._ax.plot(
                data['values']['x'],
                data['values']['y'],
                label=self.label,
                zorder=10,
                **{**default_plot_style, **kwargs},
            )[0]
            self._mask = self._ax.plot(
                data['mask']['x'],
                data['mask']['y'],
                zorder=11,
                mec=mask_color,
                mfc="None",
                mew=3.0,
                linestyle="none",
                marker=self._line.get_marker(),
                visible=data['mask']['visible'],
            )[0]

        line_mask = ~np.isnan(data['mask']['y'])
        self._line._plopp_mask = line_mask

        # Add error bars
        if errorbars and (data['stddevs'] is not None):
            self._error = self._ax.errorbar(
                data['stddevs']['x'],
                data['stddevs']['y'],
                yerr=data['stddevs']['e'],
                color=self._line.get_color(),
                zorder=10,
                fmt="none",
            )
            # Set the selection mask on the line collection that makes the segments
            self._error[2][0]._plopp_mask = line_mask[1:] if data["hist"] else line_mask

        if self.label and self._canvas._legend:
            leg_args = {}
            if isinstance(self._canvas._legend, (list, tuple)):
                leg_args = {'loc': self._canvas._legend}
            elif not isinstance(self._canvas._legend, bool):
                raise TypeError(
                    "Legend must be a bool, tuple, or a list, "
                    f"not {type(self._canvas._legend)}"
                )
            self._ax.legend(**leg_args)

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
                    new_values['stddevs']['x'],
                    new_values['stddevs']['y'],
                    new_values['stddevs']['e'],
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
