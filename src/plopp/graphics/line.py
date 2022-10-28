# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core.utils import merge_masks
from .canvas import Canvas

import scipp as sc
import numpy as np
from numpy.typing import ArrayLike
from typing import Dict
from matplotlib.lines import Line2D


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

        self._ax = canvas.ax
        self._data = data

        args = _parse_dicts_in_kwargs(kwargs, name=data.name)

        self._line = None
        self._mask = None
        self._error = None
        self._dim = None
        self._unit = None
        self.label = data.name

        self._dim = self._data.dim
        self._unit = self._data.unit
        self._coord = self._data.meta[self._dim]

        aliases = {'ls': 'linestyle', 'lw': 'linewidth', 'c': 'color'}
        for key, alias in aliases.items():
            if key in args:
                args[alias] = args.pop(key)

        self._make_line(data=self._make_data(), number=number, **args)

    def _make_line(self,
                   data: Dict,
                   number: int,
                   errorbars: bool = True,
                   mask_color: str = 'black',
                   **kwargs):
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
        has_mask = data["mask"] is not None
        mask_data_key = "mask" if has_mask else "values"

        default_step_style = {
            'linestyle': 'solid',
            'linewidth': 1.5,
            'color': f'C{number}'
        }
        markers = list(Line2D.markers.keys())
        default_plot_style = {
            'linestyle': 'none',
            'linewidth': 1.5,
            'marker': markers[(number + 2) % len(markers)],
            'color': f'C{number}'
        }

        if data["hist"]:
            self._line = self._ax.step(data["values"]["x"],
                                       data["values"]["y"],
                                       label=self.label,
                                       zorder=10,
                                       **{
                                           **default_step_style,
                                           **kwargs
                                       })[0]

            self._mask = self._ax.step(data["values"]["x"], data[mask_data_key]["y"])[0]
            self._mask.update_from(self._line)
            self._mask.set_color(mask_color)
            self._mask.set_label(None)
            self._mask.set_linewidth(self._mask.get_linewidth() * 3)
            self._mask.set_zorder(self._mask.get_zorder() - 1)
            self._mask.set_visible(has_mask)
        else:
            self._line = self._ax.plot(data["values"]["x"],
                                       data["values"]["y"],
                                       label=self.label,
                                       zorder=10,
                                       **{
                                           **default_plot_style,
                                           **kwargs
                                       })[0]
            self._mask = self._ax.plot(data["values"]["x"],
                                       data[mask_data_key]["y"],
                                       zorder=11,
                                       mec=mask_color,
                                       mfc="None",
                                       mew=3.0,
                                       linestyle="none",
                                       marker=self._line.get_marker(),
                                       visible=has_mask)[0]

        # Add error bars
        if errorbars and ("e" in data["variances"]):
            self._error = self._ax.errorbar(data["variances"]["x"],
                                            data["variances"]["y"],
                                            yerr=data["variances"]["e"],
                                            color=self._line.get_color(),
                                            zorder=10,
                                            fmt="none")

    def _preprocess_hist(self, data: dict) -> dict:
        """
        Convert 1d data to be plotted to internal format, e.g., padding
        histograms and duplicating info for variances.
        """
        x = data["values"]["x"]
        y = data["values"]["y"]
        hist = len(x) != len(y)
        if hist:
            data["values"]["y"] = np.concatenate((y[0:1], y))
            if data["mask"] is not None:
                data["mask"]["y"] = np.concatenate(
                    (data["mask"]["y"][0:1], data["mask"]["y"]))
        if self._data.variances is not None:
            data["variances"]["x"] = 0.5 * (x[1:] + x[:-1]) if hist else x
        data["variances"]["y"] = y
        data["hist"] = hist
        return data

    def _make_data(self) -> dict:
        data = {"values": {}, "variances": {}, "mask": None}
        data["values"]["x"] = self._data.meta[self._dim].values
        data["values"]["y"] = self._data.values
        if self._data.variances is not None:
            data["variances"]["e"] = sc.stddevs(self._data.data).values
        if len(self._data.masks):
            one_mask = merge_masks(self._data.masks).values
            data["mask"] = {
                "y": np.where(one_mask, data["values"]["y"], None).astype(np.float32)
            }
        return self._preprocess_hist(data)

    def update(self, new_values: sc.DataArray):
        """
        Update the x and y positions of the data points from new data.

        Parameters
        ----------
        new_values:
            New data to update the line values, masks, errorbars from.
        """
        self._data = new_values
        new_values = self._make_data()

        self._line.set_data(new_values["values"]["x"], new_values["values"]["y"])
        if new_values["mask"] is not None:
            self._mask.set_data(new_values["values"]["x"], new_values["mask"]["y"])
            self._mask.set_visible(True)
        else:
            self._mask.set_visible(False)

        if (self._error is not None) and ("e" in new_values["variances"]):
            coll = self._error.get_children()[0]
            coll.set_segments(
                self._change_segments_y(new_values["variances"]["x"],
                                        new_values["variances"]["y"],
                                        new_values["variances"]["e"]))

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
            self._error.set_color(val)
