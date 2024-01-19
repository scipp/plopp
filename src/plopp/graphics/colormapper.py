# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from collections.abc import Iterable
from copy import copy
from functools import reduce
from typing import Any, Literal, Optional, Tuple, Union

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import scipp as sc
from matplotlib.colorbar import ColorbarBase
from matplotlib.colors import Colormap, LinearSegmentedColormap, LogNorm, Normalize

from ..backends.matplotlib.utils import fig_to_bytes
from ..core.limits import find_limits, fix_empty_range
from ..core.utils import maybe_variable_to_number, merge_masks


def _get_cmap(name: str, nan_color: str = None) -> Colormap:
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
    autoscale:
        The behavior of the color range limits. If ``auto``, the limits automatically
        adjusts every time the data changes. If ``grow``, the limits are allowed to
        grow with time but they do not shrink.
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
        canvas: Optional[Any] = None,
        cbar: bool = True,
        cmap: str = 'viridis',
        mask_cmap: str = 'gray',
        norm: Literal['linear', 'log'] = 'linear',
        autoscale: Literal['auto', 'grow'] = 'auto',
        vmin: Optional[Union[sc.Variable, int, float]] = None,
        vmax: Optional[Union[sc.Variable, int, float]] = None,
        nan_color: Optional[str] = None,
        figsize: Optional[Tuple[float, float]] = None,
    ):
        self.cax = canvas.cax if canvas is not None else None
        self.cmap = _get_cmap(cmap, nan_color=nan_color)
        self.mask_cmap = _get_cmap(mask_cmap, nan_color=nan_color)
        self.user_vmin = vmin
        self.user_vmax = vmax
        self.vmin = np.inf
        self.vmax = np.NINF
        self.norm = norm
        self._autoscale = autoscale

        # Note that we need to set vmin/vmax for the LogNorm, if not an error is
        # raised when making the colorbar before any call to update is made.
        self.normalizer = _get_normalizer(self.norm)
        self.colorbar = None
        self.unit = None

        self.name = None
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

    def __setitem__(self, key: str, artist: Any):
        self.artists[key] = artist

    def __getitem__(self, key: str) -> Any:
        return self.artists[key]

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
            one_mask = merge_masks(data.masks).values
            colors[one_mask] = self.mask_cmap(self.normalizer(data.values[one_mask]))
        return colors

    def autoscale(self):
        """
        Re-compute the global min and max range of values by iterating over all the
        artists. If autoscale is set to ``'auto'``, the limits adjust to he current
        range. If it is set to ``'grow'``, limits can grow but not shrink.
        """
        limits = [
            fix_empty_range(find_limits(artist._data, scale=self.norm))
            for artist in self.artists.values()
        ]
        vmin = reduce(min, [v[0] for v in limits])
        vmax = reduce(max, [v[1] for v in limits])
        if self.user_vmin is not None:
            self.vmin = self.user_vmin
        elif (vmin.value < self.vmin) or (self._autoscale == 'auto'):
            self.vmin = vmin.value
        if self.user_vmax is not None:
            self.vmax = self.user_vmax
        elif (vmax.value > self.vmax) or (self._autoscale == 'auto'):
            self.vmax = vmax.value

        if self.vmin >= self.vmax:
            if self.user_vmax is not None:
                self.vmax = self.user_vmax
                self.vmin = self.user_vmax - abs(self.user_vmax) * 0.1
            else:
                self.vmin = self.user_vmin
                self.vmax = self.user_vmin + abs(self.user_vmin) * 0.1

    def _set_artists_colors(self, keys: Iterable):
        """
        Update the colors of all the artists apart from the one that triggered the
        update, as those get updated by the figure.

        Parameters
        ----------
        keys:
            List of artists to update.
        """
        for k in keys:
            self.artists[k].set_colors(self.rgba(self.artists[k].data))

    def _set_normalizer_limits(self):
        """
        Synchronize the underlying normalizer limits to the current state.
        """
        # Note that the order matters here, as for a normalizer vmin cannot be set above
        # the current vmax.
        if self.vmin >= self.normalizer.vmax:
            self.normalizer.vmax = self.vmax
            self.normalizer.vmin = self.vmin
        else:
            self.normalizer.vmin = self.vmin
            self.normalizer.vmax = self.vmax

    def update(self, key: str, data: sc.DataArray):
        """
        Update the colorscale bounds taking into account new values.
        We also update the colorbar widget if it exists.

        Parameters
        ----------
        data:
            The data array to use to update the colorscale range.
        key:
            The id of the node that provided this data.
        """
        if self.name is None:
            self.name = data.name
            # If name is None, this is the first time update is called
            if self.user_vmin is not None:
                self.user_vmin = maybe_variable_to_number(
                    self.user_vmin, unit=self.unit
                )
            if self.user_vmax is not None:
                self.user_vmax = maybe_variable_to_number(
                    self.user_vmax, unit=self.unit
                )
        elif data.name != self.name:
            self.name = ''
        if self.cax is not None:
            text = self.name
            if self.unit is not None:
                text += f'{" " if self.name else ""}[{self.unit}]'
            self.cax.set_ylabel(text)
        old_bounds = np.array([self.vmin, self.vmax])
        self.autoscale()
        self._set_normalizer_limits()

        if not np.allclose(old_bounds, np.array([self.vmin, self.vmax])):
            self._update_colorbar_widget()
            keys = self.artists.keys()
        else:
            keys = [key]
        self._set_artists_colors(keys)

    def toggle_norm(self):
        """
        Toggle the norm flag, between `linear` and `log`.
        """
        self.norm = "log" if self.norm == 'linear' else 'linear'
        self.normalizer = _get_normalizer(self.norm)
        self.vmin = np.inf
        self.vmax = np.NINF
        self.autoscale()
        self._set_normalizer_limits()
        self._set_artists_colors(self.artists.keys())
        if self.colorbar is not None:
            self.colorbar.mappable.norm = self.normalizer
            self._update_colorbar_widget()
