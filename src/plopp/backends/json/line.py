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


class Line:
    """ """

    def __init__(
        self,
        canvas: Canvas,
        data: sc.DataArray,
        uid: str | None = None,
        artist_number: int = 0,
        errorbars: bool = True,
        mask_color: str | None = None,
        color: str | None = None,
        linestyle: str | None = None,
        marker: str | None = None,
        markerfacecolor: str | None = None,
        markeredgecolor: str | None = None,
        markersize: float | None = None,
        markeredgewidth: float | None = None,
        zorder: int | None = None,
        visible: bool = True,
        opacity: float = 1.0,
    ):
        check_ndim(data, ndim=1, origin='Line')
        self.uid = uid if uid is not None else uuid.uuid4().hex
        self._canvas = canvas
        self._data = data

        # line_args = parse_dicts_in_kwargs(kwargs, name=data.name)

        self._line = None
        self._mask = None
        self._error = None
        self._unit = None
        self.label = data.name
        self._dim = self._data.dim
        self._unit = self._data.unit
        self._coord = self._data.coords[self._dim]
        if mask_color is None:
            mask_color = 'black'

        # aliases = {'ls': 'linestyle', 'lw': 'linewidth', 'c': 'color'}
        # for key, alias in aliases.items():
        #     if key in line_args:
        #         line_args[alias] = line_args.pop(key)

        line_data = make_line_data(data=self._data, dim=self._dim)

        markers = list(Line2D.markers.keys())

        if line_data["hist"]:
            self._line = {
                "kind": "step",
                "x": line_data['values']['x'],
                "y": line_data['values']['y'],
                "label": self.label,
                "linestyle": linestyle or "solid",
                "color": color or f"C{artist_number}",
                "zorder": zorder or 2,
                "visible": visible,
                "opacity": opacity,
            }
            # self._mask = {
            #     "kind": "step",
            #     "x": line_data['mask']['x'],
            #     "y": line_data['mask']['y'],
            #     "linestyle": linestyle or "solid",
            #     "color": mask_color,
            #     "zorder": (zorder or 2) - 1,
            #     "visible": visible,
            #     "opacity": opacity,
            # }
        else:
            self._line = {
                "kind": "line",
                "x": line_data['values']['x'],
                "y": line_data['values']['y'],
                "label": self.label,
                "linestyle": linestyle or "none",
                "marker": marker or markers[(artist_number + 2) % len(markers)],
                "color": color or f"C{artist_number}",
                "zorder": zorder or 2,
                "visible": visible,
                "opacity": opacity,
            }
            # self._mask = {
            #     "kind": "line",
            #     "x": line_data['mask']['x'],
            #     "y": line_data['mask']['y'],
            #     "linestyle": linestyle or "none",
            #     "marker": marker or markers[(artist_number + 2) % len(markers)],
            #     "color": mask_color,
            #     "zorder": (zorder or 2) + 1,
            #     "visible": visible,
            #     "opacity": opacity,
            # }

        # Add error bars
        if errorbars and (line_data['stddevs'] is not None):
            self._line["e"] = line_data['stddevs']['e']

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

        self._line.update(x=line_data['values']['x'], y=line_data['values']['y'])
        # self._mask.update(x=line_data['mask']['x'], y=line_data['mask']['y'])

        if ("e" in self._line) and (line_data['stddevs'] is not None):
            self._line["e"] = line_data['stddevs']['e']

    def remove(self):
        """
        Remove the line, masks and errorbar artists from the canvas.
        """
        pass

    @property
    def color(self) -> str:
        """
        The line color.
        """
        return self._line.get("color", None)

    @color.setter
    def color(self, val: str):
        self._line["color"] = val

    @property
    def style(self) -> str:
        """
        The line style.
        """
        return self._line.get("linestyle", None)

    @style.setter
    def style(self, val: str):
        self._line["linestyle"] = val

    @property
    def width(self) -> float:
        """
        The line width.
        """
        return self._line.get("linewidth", None)

    @width.setter
    def width(self, val: float):
        self._line["linewidth"] = val

    @property
    def marker(self) -> str:
        """
        The line marker.
        """
        return self._line.get("marker", None)

    @marker.setter
    def marker(self, val: str):
        self._line["marker"] = val
        # self._mask["marker"] = val

    @property
    def visible(self) -> bool:
        """
        Whether the line is visible.
        """
        return self._line.get("visible", None)

    @visible.setter
    def visible(self, val: bool):
        self._line["visible"] = val
        # self._mask["visible"] = val

    @property
    def opacity(self) -> float:
        """
        The line opacity.
        """
        return self._line.get("opacity", None)

    @opacity.setter
    def opacity(self, val: float):
        self._line["opacity"] = val

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
            errorbars="e" in self._line,
            xscale=xscale,
            yscale=yscale,
        )
