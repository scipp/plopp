# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import uuid
from enum import Enum
from typing import Literal

import numpy as np
import scipp as sc
from matplotlib.axes import Axes
from matplotlib.dates import date2num
from matplotlib.lines import Line2D

from ...graphics.bbox import BoundingBox
from ..common import check_ndim, make_line_bbox, make_line_data
from .canvas import Canvas
from .utils import parse_dicts_in_kwargs


def _to_float(x):
    return date2num(x) if np.issubdtype(x.dtype, np.datetime64) else x


ErrorbarMode = Enum("ErrorbarMode", [("band", 1), ("bar", 2)])


class Errorbars:
    """
    Artist to represent error bars for one-dimensional data.
    """

    def __init__(
        self,
        mode: Literal["band", "bar"],
        ax: Axes,
        x: np.ndarray,
        y: np.ndarray,
        e: np.ndarray,
        color,
        zorder,
    ):
        self._mode = ErrorbarMode[mode]
        if self._mode == ErrorbarMode.band:
            self._artist = ax.fill_between(
                x, y - e, y + e, color=color, alpha=0.3, zorder=zorder - 1
            )
        elif self._mode == ErrorbarMode.bar:
            self._artist = ax.errorbar(
                x, y, yerr=e, color=color, zorder=zorder, fmt="none"
            )
        else:
            raise ValueError(f"Invalid errorbar mode: {mode}")

    def update(self, x: np.ndarray, y: np.ndarray, e: np.ndarray) -> None:
        if self._mode == ErrorbarMode.band:
            verts = self._artist.get_paths()[0].vertices
            if len(x) != (len(verts) - 3) // 2:
                # We need to recreate the artist if the number of points has changed
                color = self._artist.get_facecolor()[0]
                alpha = self._artist.get_alpha()
                zorder = self._artist.get_zorder()
                self._artist.remove()
                self._artist = self._artist.axes.fill_between(
                    x, y - e, y + e, color=color, alpha=alpha, zorder=zorder
                )
            else:
                yme = y - e
                ype = y + e
                verts[:, 0] = np.concatenate([x[0:1], x, [x[-1]], x[::-1], x[0:1]])
                verts[:, 1] = np.concatenate(
                    [ype[0:1], yme, [ype[-1]], ype[::-1], yme[0:1]]
                )
        else:
            coll = self._artist.get_children()[0]
            x, y, e = (_to_float(z) for z in (x, y, e))
            arr1 = np.repeat(x, 2)
            arr2 = np.array([y - e, y + e]).T.flatten()
            coll.set_segments(np.array([arr1, arr2]).T.flatten().reshape(len(y), 2, 2))

    def remove(self):
        self._artist.remove()

    def set_color(self, color):
        if self._mode == ErrorbarMode.band:
            self._artist.set_facecolor(color)
        else:
            for artist in self._artist.get_children():
                artist.set_color(color)

    def set_visible(self, visible):
        if self._mode == ErrorbarMode.band:
            self._artist.set_visible(visible)
        else:
            for artist in self._artist.get_children():
                artist.set_visible(visible)

    def set_alpha(self, alpha):
        if self._mode == ErrorbarMode.band:
            self._artist.set_alpha(alpha)
        else:
            for artist in self._artist.get_children():
                artist.set_alpha(alpha)


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
        Whether to add error bars to the line. Optionally, this can be a string to
        specify the error bar style. Valid values are 'band' and 'bar'.
    mask_color:
        The color of the masked points.
    """

    def __init__(
        self,
        canvas: Canvas,
        data: sc.DataArray,
        uid: str | None = None,
        artist_number: int = 0,
        errorbars: Literal['band', 'bar', True, False] = True,
        mask_color: str | None = None,
        **kwargs,
    ):
        check_ndim(data, ndim=1, origin='Line')
        self.uid = uid if uid is not None else uuid.uuid4().hex
        self._canvas = canvas
        self._ax = self._canvas.ax
        self._data = data
        if errorbars is True:
            errorbars = 'bar'

        line_args = parse_dicts_in_kwargs(kwargs, name=data.name)

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

        aliases = {'ls': 'linestyle', 'lw': 'linewidth', 'c': 'color'}
        for key, alias in aliases.items():
            if key in line_args:
                line_args[alias] = line_args.pop(key)

        line_data = make_line_data(data=self._data, dim=self._dim)

        default_step_style = {
            'linestyle': 'solid',
            'linewidth': 1.5,
            'color': f'C{artist_number}',
            'zorder': 2,
        }
        markers = list(Line2D.markers.keys())
        default_plot_style = {
            'linestyle': 'none',
            'linewidth': 1.5,
            'marker': markers[(artist_number + 2) % len(markers)],
            'color': f'C{artist_number}',
            'zorder': 2,
        }

        if line_data["hist"]:
            self._line = self._ax.step(
                line_data['values']['x'],
                line_data['values']['y'],
                label=self.label,
                **{**default_step_style, **line_args},
            )[0]

            self._mask = self._ax.step(line_data['mask']['x'], line_data['mask']['y'])[
                0
            ]
        else:
            self._line = self._ax.plot(
                line_data['values']['x'],
                line_data['values']['y'],
                label=self.label,
                **{**default_plot_style, **line_args},
            )[0]
            self._mask = self._ax.plot(line_data['mask']['x'], line_data['mask']['y'])[
                0
            ]

        self._mask.update_from(self._line)
        self._mask.set_color(mask_color)
        self._mask.set_label(None)
        self._mask.set_visible(line_data['mask']['visible'])
        if self._line.get_marker().lower() != 'none':
            self._mask.set(
                mec=mask_color, mfc='None', mew=3.0, zorder=self._line.get_zorder() + 1
            )
        if self._line.get_linestyle().lower() != 'none':
            self._mask.set(
                lw=self._line.get_linewidth() * 3, zorder=self._line.get_zorder() - 1
            )

        # Add error bars
        if errorbars and (line_data['stddevs'] is not None):
            self._error = Errorbars(
                mode=errorbars,
                ax=self._ax,
                x=line_data['stddevs']['x'],
                y=line_data['stddevs']['y'],
                e=line_data['stddevs']['e'],
                color=self._line.get_color(),
                zorder=self._line.get_zorder(),
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

        self._line.set_data(line_data['values']['x'], line_data['values']['y'])
        self._mask.set_data(line_data['mask']['x'], line_data['mask']['y'])
        self._mask.set_visible(line_data['mask']['visible'])

        if (self._error is not None) and (line_data['stddevs'] is not None):
            self._error.update(
                line_data['stddevs']['x'],
                line_data['stddevs']['y'],
                line_data['stddevs']['e'],
            )

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
    def color(self) -> str:
        """
        The line color.
        """
        return self._line.get_color()

    @color.setter
    def color(self, val: str):
        self._line.set_color(val)
        if self._error is not None:
            self._error.set_color(val)
        self._canvas.draw()

    @property
    def style(self) -> str:
        """
        The line style.
        """
        return self._line.get_linestyle()

    @style.setter
    def style(self, val: str):
        self._line.set_linestyle(val)
        self._canvas.draw()

    @property
    def width(self) -> float:
        """
        The line width.
        """
        return self._line.get_linewidth()

    @width.setter
    def width(self, val: float):
        self._line.set_linewidth(val)
        self._canvas.draw()

    @property
    def marker(self) -> str:
        """
        The line marker.
        """
        return self._line.get_marker()

    @marker.setter
    def marker(self, val: str):
        self._line.set_marker(val)
        self._mask.set_marker(val)
        self._canvas.draw()

    @property
    def visible(self) -> bool:
        """
        Whether the line is visible.
        """
        return self._line.get_visible()

    @visible.setter
    def visible(self, val: bool):
        self._line.set_visible(val)
        self._mask.set_visible(val)
        if self._error is not None:
            self._error.set_visible(val)
        self._canvas.draw()

    @property
    def opacity(self) -> float:
        """
        The line opacity.
        """
        return self._line.get_alpha()

    @opacity.setter
    def opacity(self, val: float):
        self._line.set_alpha(val)
        self._mask.set_alpha(val)
        if self._error is not None:
            self._error.set_alpha(val)
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
