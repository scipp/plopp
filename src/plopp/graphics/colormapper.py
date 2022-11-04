# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core.limits import find_limits, fix_empty_range
from ..core.utils import merge_masks, maybe_variable_to_number
from .utils import fig_to_bytes, silent_mpl_figure

from copy import copy
import matplotlib as mpl
from matplotlib.colors import Normalize, LogNorm, LinearSegmentedColormap, Colormap
import matplotlib.pyplot as plt
from matplotlib.colorbar import ColorbarBase
import numpy as np
import scipp as sc
from typing import Literal, Tuple, Union


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


class ColorMapper:
    """
    A class that handles conversion between data values and RGBA colors.
    It controls the normalization (linear or log), as well as the min and max limits
    for the color range.
    If the min and max values are not set manually by the user, they are allowed to grow
    with time but they do not shrink.

    Parameters
    ----------
    cax:
        The axes to use for the colorbar. If none are supplied, the ColorMapper will
        create its own axes.
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

    def __init__(self,
                 cax: plt.Axes = None,
                 cmap: str = 'viridis',
                 mask_cmap: str = 'gray',
                 norm: Literal['linear', 'log'] = 'linear',
                 vmin: Union[sc.Variable, int, float] = None,
                 vmax: Union[sc.Variable, int, float] = None,
                 nan_color: str = None,
                 figsize: Tuple[float, float] = None):

        self.cax = cax
        self.cmap = _get_cmap(cmap, nan_color=nan_color)
        self.mask_cmap = _get_cmap(mask_cmap, nan_color=nan_color)
        self.user_vmin = vmin
        self.user_vmax = vmax
        self.vmin = np.inf
        self.vmax = np.NINF
        self.norm = norm

        # Note that we need to set vmin/vmax for the LogNorm, if not an error is
        # raised when making the colorbar before any call to update is made.
        self.normalizer = Normalize() if self.norm == 'linear' else LogNorm(vmin=1,
                                                                            vmax=2)
        self.colorbar = None
        self.unit = None
        self.name = None
        self.changed = False
        self.artists = {}
        self.widget = None

        if self.cax is None:
            dpi = 100
            height_inches = (figsize[1] / dpi) if figsize is not None else 6
            with silent_mpl_figure():
                fig = plt.figure(figsize=(height_inches * 0.2, height_inches))
            self.cax = fig.add_axes([0.05, 0.02, 0.2, 0.98])

        self.colorbar = ColorbarBase(self.cax, cmap=self.cmap, norm=self.normalizer)
        self.cax.yaxis.set_label_coords(-0.9, 0.5)

    def __setitem__(self, key, val):
        self.artists[key] = val

    def __getitem__(self, key):
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

    def autoscale(self, data: sc.DataArray):
        """
        Re-compute the min and max range of values, given new values.
        The current range can grow but not shrink.

        Parameters
        ----------
        data:
            The data array containing the values to update the current range.
        """
        vmin, vmax = fix_empty_range(find_limits(data, scale=self.norm))
        if self.user_vmin is not None:
            self.vmin = maybe_variable_to_number(self.user_vmin, unit=self.unit)
        elif vmin.value < self.vmin:
            self.vmin = vmin.value
        if self.user_vmax is not None:
            self.vmax = maybe_variable_to_number(self.user_vmax, unit=self.unit)
        elif vmax.value > self.vmax:
            self.vmax = vmax.value

    def _set_artists_colors(self, key: str = None):
        """
        Update the colors of all the artists apart from the one that triggered the
        update, as those get updated by the figure.

        Parameters
        ----------
        key:
            Update all connected artists, apart from the one whose id is ``key``.
        """
        keys = set(self.artists.keys())
        if key is not None:
            keys -= {key}
        for k in keys:
            self.artists[k].set_colors(self.rgba(self.artists[k].data))

    def update(self, data: sc.DataArray, key: str):
        """
        Update the colorscale bounds taking into account new values.
        If the bounds have changed, we update all the colors in the artists that depend
        on this ColorMapper. We also update the colorbar widget if it exists.

        Parameters
        ----------
        data:
            The data array to use to update the colorscale range.
        key:
            The id of the node that provided this data.
        """
        if self.unit is None:
            self.unit = data.unit
            self.name = data.name
            self.cax.set_ylabel(f'{self.name} [{self.unit}]')
        elif data.unit != self.unit:
            raise ValueError(f'Incompatible unit: colormapper has unit {self.unit}, '
                             f'new data has unit {data.unit}.')

        old_bounds = np.array([self.vmin, self.vmax])
        self.autoscale(data=data)

        # Note that the order matters here, as for a normalizer vmin cannot be set above
        # the current vmax.
        if self.vmin > self.normalizer.vmax:
            self.normalizer.vmax = self.vmax
            self.normalizer.vmin = self.vmin
        else:
            self.normalizer.vmin = self.vmin
            self.normalizer.vmax = self.vmax

        if not np.allclose(old_bounds, np.array([self.vmin, self.vmax])):
            self._set_artists_colors(key=key)
            self._update_colorbar_widget()

    def toggle_norm(self):
        """
        Toggle the norm flag, between `linear` and `log`.
        """
        self.norm = "log" if self.norm == 'linear' else 'linear'
        self.normalizer = Normalize() if self.norm == 'linear' else LogNorm()
        self.vmin = np.inf
        self.vmax = np.NINF
        for artist in self.artists.values():
            self.autoscale(data=artist._data)
        self.normalizer.vmin = self.vmin
        self.normalizer.vmax = self.vmax
        self._set_artists_colors()
        self.colorbar.mappable.norm = self.normalizer
        self._update_colorbar_widget()
