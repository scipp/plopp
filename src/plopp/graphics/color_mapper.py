# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core.limits import find_limits, fix_empty_range
from ..core.utils import merge_masks
from ..widgets import ToggleTool
from .io import fig_to_bytes

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
                 notify_on_change=None,
                 cmap: str = 'viridis',
                 mask_cmap: str = 'gray',
                 norm: str = "linear",
                 vmin=None,
                 vmax=None,
                 nan_color=None,
                 figheight=None):
        self.cmap = _get_cmap(cmap, nan_color=nan_color)
        self.mask_cmap = _get_cmap(mask_cmap, nan_color=nan_color)
        self.user_vmin = vmin
        self.user_vmax = vmax
        # self._vmin = {'linear': np.inf, 'log': np.inf}
        # self._vmax = {'linear': np.NINF, 'log': np.NINF}
        self.vmin = np.inf
        self.vmax = np.NINF
        self.norm = norm
        # self.normalizer = {'linear': Normalize(), 'log': LogNorm()}
        self.normalizer = Normalize() if self.norm == "linear" else LogNorm()
        self._notify_on_change = [notify_on_change]
        self.colorbar = None
        self.unit = None
        self.name = None
        self._figheight = figheight
        self.bounds_changed = False

    def to_widget(self):
        import ipywidgets as ipw
        self.colorbar = {
            'image':
            ipw.HTML(),
            'button':
            ToggleTool(self.toggle_norm,
                       value=self._norm == 'log',
                       description='log',
                       tooltip='Toggle data norm').widget
        }
        self._update_colorbar()
        return ipw.VBox(list(self.colorbar.values()))

    def _update_colorbar(self):
        # Choose a dpi that makes the sizes in inches (mpl colorbar) and pixels
        # (pythreejs renderer) match.
        dpi = 100
        # Additional shrinking factor to make space for the 'log' toggle button
        height_inches = 0.88 * self._figheight / dpi
        cbar_fig = plt.figure(figsize=(height_inches * 0.2, height_inches))
        cbar_ax = cbar_fig.add_axes([0.05, 0.02, 0.25, 1.0])
        _ = ColorbarBase(cbar_ax, cmap=self.cmap, norm=self.norm)
        cbar_ax.set_ylabel(f'{self.name} [{self.unit}]')
        self.colorbar['image'].value = fig_to_bytes(cbar_fig, form='svg').decode()
        plt.close(cbar_fig)

    def rgba(self, data: sc.DataArray):
        """
        Return rgba values given a data array.
        """
        colors = self.cmap(self.normalizer(data.values))
        if data.masks:
            one_mask = merge_masks(data.masks).values
            colors[one_mask] = self.mask_cmap(self.normalizer(data.values[one_mask]))
        return colors

    def autoscale(self, data=None):
        """
        Re-compute the min and max range of values, given new values.
        """
        if data is not None:
            self._data = data
        old_bounds = np.array([self.vmin, self.vmax])
        vmin, vmax = fix_empty_range(find_limits(self._data, scale=self._norm))
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

        self.normalizer.vmin = self._vmin
        self.normalizer.vmax = self._vmax

        self.bounds_changed = not np.allclose(old_bounds,
                                              np.array([self.vmin, self.vmax]))

        # if (self.colorbar is not None) and not np.allclose(
        #         old_bounds, np.array([self.vmin, self.vmax])):
        #     self._update_colorbar()

    # def rescale(self, data):
    #     old_bounds = np.array([self.vmin, self.vmax])
    #     self.autoscale(data=data, scale=self._norm)
    #     if (self.colorbar is not None) and not np.allclose(
    #             old_bounds, np.array([self.vmin, self.vmax])):
    #         self._update_colorbar()

    def set_norm(self, data):
        """
        Set the norm of the color mapper and update the min/max values.
        """
        self.unit = data.unit
        self.name = data.name
        self.autoscale(data=data.data, scale='linear')
        self.autoscale(data=data.data, scale='log')
        # self.notify()

    def toggle_norm(self):
        """
        Toggle the norm flag, between `linear` and `log`.
        """
        self.norm = "log" if self.norm == "linear" else "linear"
        self.normalizer = Normalize() if self.norm == "linear" else LogNorm()
        # print(self._vmin, self._vmax)
        # print(self.norm.vmin, self.norm.vmax)
        # self.notify()
        if self.colorbar is not None:
            self._update_colorbar()

    def add_notify(self, callback):
        self._notify_on_change.append(callback)

    def notify(self):
        for callback in self._notify_on_change:
            callback()

    # @property
    # def vmin(self):
    #     return self._vmin[self._norm]

    # @property
    # def vmax(self):
    #     return self._vmax[self._norm]

    # @property
    # def norm(self):
    #     return self.normalizer[self._norm]
