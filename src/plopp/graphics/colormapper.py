# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core.limits import find_limits, fix_empty_range
from ..core.utils import merge_masks
from .utils import fig_to_bytes, silent_mpl_figure

import matplotlib as mpl
from matplotlib.colors import Normalize, LogNorm, LinearSegmentedColormap
import matplotlib.pyplot as plt
from matplotlib.colorbar import ColorbarBase
import scipp as sc
from copy import copy
import numpy as np


def _get_cmap(name, nan_color=None):

    try:
        if hasattr(mpl, 'colormaps'):
            cmap = copy(mpl.colormaps[name])
        else:
            cmap = mpl.cm.get_cmap(name)
    except (KeyError, ValueError):
        cmap = LinearSegmentedColormap.from_list("tmp", [name, name])
    # TODO: we need to set under and over values for the cmap with
    # `cmap.set_under` and `cmap.set_over`. Ideally these should come from a config?
    if nan_color is not None:
        cmap.set_bad(color=nan_color)
    return cmap


class ColorMapper:

    def __init__(self,
                 cax=None,
                 cmap: str = 'viridis',
                 mask_cmap: str = 'gray',
                 norm: str = "linear",
                 vmin=None,
                 vmax=None,
                 nan_color=None,
                 figsize=None):

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
        self.normalizer = Normalize() if self.norm == "linear" else LogNorm(vmin=1,
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
            self.cax = fig.add_axes([0.05, 0.02, 0.2, 1.0])

        self.colorbar = ColorbarBase(self.cax, cmap=self.cmap, norm=self.normalizer)
        self.cax.yaxis.set_label_coords(-1.1, 0.5)

    def __setitem__(self, key, val):
        self.artists[key] = val

    def __getitem__(self, key):
        return self.artists[key]

    def to_widget(self):
        import ipywidgets as ipw
        self.widget = ipw.HTML()
        self._update_colorbar_widget()
        return self.widget

    def _update_colorbar_widget(self):
        if self.widget is not None:
            self.widget.value = fig_to_bytes(self.cax.get_figure(), form='svg').decode()

    def rgba(self, data: sc.DataArray):
        """
        Return rgba values given a data array.
        """
        colors = self.cmap(self.normalizer(data.values))
        if data.masks:
            one_mask = merge_masks(data.masks).values
            colors[one_mask] = self.mask_cmap(self.normalizer(data.values[one_mask]))
        return colors

    def autoscale(self, data):
        """
        Re-compute the min and max range of values, given new values.
        """
        vmin, vmax = fix_empty_range(find_limits(data, scale=self.norm))
        if self.user_vmin is not None:
            assert self.user_vmin.unit == data.unit
            self.vmin = self.user_vmin.value
        elif vmin.value < self.vmin:
            self.vmin = vmin.value
        if self.user_vmax is not None:
            assert self.user_vmax.unit == data.unit
            self.vmax = self.user_vmax.value
        elif vmax.value > self.vmax:
            self.vmax = vmax.value

    def _set_artists_colors(self, key=None):
        """
        Update the colors of all the artists apart from the one that triggered the
        update, as those get updated by the figure.
        """
        keys = set(self.artists.keys())
        if key is not None:
            keys -= set([key])
        for k in keys:
            self.artists[k].set_colors(self.rgba(self.artists[k].data))

    def update(self, data, key):
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

        if self.unit is None:
            self.unit = data.unit
            self.name = data.name
            self.cax.set_ylabel(f'{self.name} [{self.unit}]')

        if not np.allclose(old_bounds, np.array([self.vmin, self.vmax])):
            self._set_artists_colors(key=key)
            self._update_colorbar_widget()

    def toggle_norm(self):
        """
        Toggle the norm flag, between `linear` and `log`.
        """
        self.norm = "log" if self.norm == "linear" else "linear"
        self.normalizer = Normalize() if self.norm == "linear" else LogNorm()
        self.vmin = np.inf
        self.vmax = np.NINF
        for artist in self.artists.values():
            self.autoscale(data=artist._data)
        self.normalizer.vmin = self.vmin
        self.normalizer.vmax = self.vmax
        self._set_artists_colors()
        self.colorbar.mappable.norm = self.normalizer
        self._update_colorbar_widget()
