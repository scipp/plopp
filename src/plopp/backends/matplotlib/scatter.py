# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import uuid

import numpy as np
import scipp as sc
from matplotlib.lines import Line2D

from ...core.utils import merge_masks
from .canvas import Canvas
from .utils import make_legend, parse_dicts_in_kwargs


class Scatter:
    """ """

    def __init__(
        self,
        canvas: Canvas,
        data: sc.DataArray,
        x: str = 'x',
        y: str = 'y',
        size: str | None = None,
        artist_number: int = 0,
        mask_color: str = 'black',
        cbar: bool = False,
        **kwargs,
    ):
        self._canvas = canvas
        self._ax = self._canvas.ax
        self._data = data
        self._x = x
        self._y = y
        self._size = size
        # Because all keyword arguments from the figure are forwarded to both the canvas
        # and the line, we need to remove the arguments that belong to the canvas.
        kwargs.pop('ax', None)

        scatter_kwargs = parse_dicts_in_kwargs(kwargs, name=data.name)

        self.label = data.name if not cbar else None
        self._unit = self._data.unit
        self._id = uuid.uuid4().hex

        markers = list(Line2D.markers.keys())
        default_plot_style = {
            'marker': markers[(artist_number + 2) % len(markers)],
        }
        if not cbar:
            default_plot_style['color'] = f'C{artist_number}'

        merged_kwargs = {**default_plot_style, **scatter_kwargs}
        if self._size is None:
            s = merged_kwargs.pop('s', None)
        else:
            s = self._data.coords[self._size].values

        self._scatter = self._ax.scatter(
            self._data.coords[self._x].values,
            self._data.coords[self._y].values,
            s=s,
            label=self.label,
            **merged_kwargs,
        )

        xmask = self._data.coords[self._x].values.copy()
        ymask = self._data.coords[self._y].values.copy()
        visible_mask = False
        if self._data.masks:
            not_one_mask = ~merge_masks(self._data.masks).values
            xmask[not_one_mask] = np.nan
            ymask[not_one_mask] = np.nan
            visible_mask = True
        self._mask = self._ax.scatter(
            xmask,
            ymask,
            s=s,
            marker=merged_kwargs['marker'],
            edgecolors=mask_color,
            facecolor="None",
            linewidth=3.0,
            zorder=self._scatter.get_zorder() + 1,
            visible=visible_mask,
        )

        if self._canvas._legend:
            leg_args = make_legend(self._canvas._legend)
            if np.shape(s) == np.shape(self._data.coords[self._x].values):
                handles, labels = self._scatter.legend_elements(prop="sizes")
                self._ax.legend(handles, labels, title="Sizes", **leg_args)
            if self.label:
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
        self._scatter.set_offsets(
            np.stack(
                [self._data.coords[self._x].values, self._data.coords[self._y].values],
                axis=1,
            )
        )
        if self._size is not None:
            self._scatter.set_sizes(self._data.coords[self._size].values)

    def remove(self):
        """
        Remove the scatter and mask artists from the canvas.
        """
        self._scatter.remove()
        self._mask.remove()

    def set_colors(self, rgba: np.ndarray):
        if self._scatter.get_array() is not None:
            self._scatter.set_array(None)
        self._scatter.set_facecolors(rgba)

    @property
    def data(self):
        """ """
        return self._data
