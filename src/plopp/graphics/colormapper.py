# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from copy import copy
from functools import reduce
from typing import Any, Literal

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import scipp as sc
from matplotlib.colorbar import ColorbarBase
from matplotlib.colors import Colormap, LinearSegmentedColormap, LogNorm, Normalize

from ..backends.matplotlib.utils import fig_to_bytes
from ..core.limits import find_limits, fix_empty_range
from ..core.utils import maybe_variable_to_number, merge_masks


def _get_cmap(name: str, nan_color: str | None = None) -> Colormap:
    """
    Get a colormap object from a colormap name.

    Parameters
    ----------
    name:
        Name of the colormap. If the name is just a single html color, this will
        create a colormap with that single color.
    nan_color:
        The color to use for NAN values.
    """

    try:
        if hasattr(mpl, 'colormaps'):
            cmap = copy(mpl.colormaps[name])
        else:
            cmap = mpl.cm.get_cmap(name)
    except (KeyError, ValueError):
        cmap = LinearSegmentedColormap.from_list('tmp', [name, name])
    # TODO: we need to set under and over values for the cmap with
    # `cmap.set_under` and `cmap.set_over`. Ideally these should come from a config?
    if nan_color is not None:
        cmap.set_bad(color=nan_color)
    return cmap


def _get_normalizer(norm: str) -> Normalize:
    """
    Get an appropriate normalizer depending on the scaling.
    """
    return Normalize(vmin=0, vmax=1) if norm == 'linear' else LogNorm(vmin=1, vmax=2)


class ColorMapper:
    """
    A class that handles conversion between data values and RGBA colors.
    It controls the normalization (linear or log), as well as the min and max limits
    for the color range.

    Parameters
    ----------
    cax:
        The axes to use for the colorbar. If none are supplied, the ColorMapper will
        create its own axes.
    cbar:
        Create a colorbar if ``True``. If ``False``, no colorbar is made even if ``cax``
        is defined.
    cmap:
        The name of the colormap for the data
        (see https://matplotlib.org/stable/tutorials/colors/colormaps.html).
        In addition to the Matplotlib docs, if the name is just a single html color,
        a colormap with that single color will be used.
    mask_cmap:
        The name of the colormap for masked data.
    norm:
        The colorscale normalization.
    vmin:
        The minimum value for the colorscale range. If a number (without a unit) is
        supplied, it is assumed that the unit is the same as the data unit.
    vmax:
        The maximum value for the colorscale range. If a number (without a unit) is
        supplied, it is assumed that the unit is the same as the data unit.
    nan_color:
        The color used for representing NAN values.
    figsize:
        The size of the figure next to which the colorbar will be displayed.
    """

    def __init__(
        self,
        canvas: Any | None = None,
        cbar: bool = True,
        cmap: str = 'viridis',
        mask_cmap: str = 'gray',
        norm: Literal['linear', 'log'] = 'linear',
        vmin: sc.Variable | float | None = None,
        vmax: sc.Variable | float | None = None,
        nan_color: str | None = None,
        figsize: tuple[float, float] | None = None,
    ):
        self._canvas = canvas
        self.cax = self._canvas.cax if hasattr(self._canvas, 'cax') else None
        self.cmap = _get_cmap(cmap, nan_color=nan_color)
        self.mask_cmap = _get_cmap(mask_cmap, nan_color=nan_color)
        self.user_vmin = vmin
        self.user_vmax = vmax
        self._vmin = np.inf
        self._vmax = -np.inf
        self.norm = norm
        self.set_colors_on_update = True

        # Note that we need to set vmin/vmax for the LogNorm, if not an error is
        # raised when making the colorbar before any call to update is made.
        self.normalizer = _get_normalizer(self.norm)
        self.colorbar = None
        self._unit = None
        self.empty = True
        self.changed = False
        self.artists = {}
        self.widget = None

        if cbar:
            if self.cax is None:
                dpi = 100
                height_inches = (figsize[1] / dpi) if figsize is not None else 6
                fig = plt.Figure(figsize=(height_inches * 0.2, height_inches))
                self.cax = fig.add_axes([0.05, 0.02, 0.2, 0.98])
            self.colorbar = ColorbarBase(self.cax, cmap=self.cmap, norm=self.normalizer)
            self.cax.yaxis.set_label_coords(-0.9, 0.5)

    def add_artist(self, key: str, artist: Any):
        self.artists[key] = artist

    def remove_artist(self, key: str):
        del self.artists[key]

    def to_widget(self):
        """
        Convert the colorbar into a widget for use with other ``ipywidgets``.
        """
        import ipywidgets as ipw

        self.widget = ipw.HTML()
        self._update_colorbar_widget()
        return self.widget

    def _update_colorbar_widget(self):
        """
        Upon an updated colorscale range, we need to update the image inside the widget.
        """
        if self.widget is not None:
            self.widget.value = fig_to_bytes(self.cax.get_figure(), form='svg').decode()

    def rgba(self, data: sc.DataArray) -> np.ndarray:
        """
        Return rgba values given a data array.

        Parameters
        ----------
        data:
            The data array to be converted to rgba colors, taking masks into account.
        """
        colors = self.cmap(self.normalizer(data.values))
        if data.masks:
            one_mask = sc.broadcast(merge_masks(data.masks), sizes=data.sizes).values
            colors[one_mask] = self.mask_cmap(self.normalizer(data.values[one_mask]))
        return colors

    def autoscale(self):
        """
        Re-compute the global min and max range of values by iterating over all the
        artists and adjust the limits.
        """
        limits = [
            fix_empty_range(find_limits(artist._data, scale=self.norm))
            for artist in self.artists.values()
        ]
        vmin = reduce(min, [v[0] for v in limits])
        vmax = reduce(max, [v[1] for v in limits])
        if self.user_vmin is not None:
            self._vmin = self.user_vmin
        else:
            self._vmin = vmin.value
        if self.user_vmax is not None:
            self._vmax = self.user_vmax
        else:
            self._vmax = vmax.value

        if self._vmin >= self._vmax:
            if self.user_vmax is not None:
                self._vmax = self.user_vmax
                self._vmin = self.user_vmax - abs(self.user_vmax) * 0.1
            else:
                self._vmin = self.user_vmin
                self._vmax = self.user_vmin + abs(self.user_vmin) * 0.1

        self.apply_limits()

    def apply_limits(self):
        # Synchronize the underlying normalizer limits to the current state.
        # Note that the order matters here, as for a normalizer vmin cannot be set above
        # the current vmax.
        if self._vmin >= self.normalizer.vmax:
            self.normalizer.vmax = self._vmax
            self.normalizer.vmin = self._vmin
        else:
            self.normalizer.vmin = self._vmin
            self.normalizer.vmax = self._vmax

        if self.colorbar is not None:
            self._update_colorbar_widget()
        self.notify_artists()

    def notify_artists(self):
        """
        Notify the artists that the state of the colormapper has changed.
        """
        for artist in self.artists.values():
            artist.notify_artist('colormap changed')

    @property
    def vmin(self) -> float:
        """
        Get or set the minimum value of the colorbar.
        """
        return self._vmin

    @vmin.setter
    def vmin(self, vmin: sc.Variable | float):
        self._vmin = maybe_variable_to_number(vmin, unit=self._unit)
        self.apply_limits()

    @property
    def vmax(self) -> float:
        """
        Get or set the maximum value of the colorbar.
        """
        return self._vmax

    @vmax.setter
    def vmax(self, vmax: sc.Variable | float):
        self._vmax = maybe_variable_to_number(vmax, unit=self._unit)
        self.apply_limits()

    @property
    def unit(self) -> str | None:
        """
        Get or set the unit of the colorbar.
        """
        return self._unit

    @unit.setter
    def unit(self, unit: str | None):
        self._unit = unit
        if self.user_vmin is not None:
            self.user_vmin = maybe_variable_to_number(self.user_vmin, unit=self._unit)
        if self.user_vmax is not None:
            self.user_vmax = maybe_variable_to_number(self.user_vmax, unit=self._unit)

    @property
    def ylabel(self) -> str | None:
        """
        Get or set the label of the colorbar axis.
        """
        if self.cax is not None:
            return self.cax.get_ylabel()

    @ylabel.setter
    def ylabel(self, lab: str):
        if self.cax is not None:
            self.cax.set_ylabel(lab)

    def toggle_norm(self):
        """
        Toggle the norm flag, between `linear` and `log`.
        """
        self.norm = "log" if self.norm == 'linear' else 'linear'
        self.normalizer = _get_normalizer(self.norm)
        self._vmin = np.inf
        self._vmax = -np.inf
        if self.colorbar is not None:
            self.colorbar.mappable.norm = self.normalizer
        self.autoscale()
        if self._canvas is not None:
            self._canvas.draw()
