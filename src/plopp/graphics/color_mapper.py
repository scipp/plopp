# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core.limits import find_limits, fix_empty_range

from matplotlib.colors import Normalize, LogNorm, LinearSegmentedColormap
from matplotlib.pyplot import colorbar
from matplotlib import cm
import scipp as sc
from copy import copy
import numpy as np


def _get_cmap(name):

    try:
        cmap = copy(cm.get_cmap(name))
    except ValueError:
        cmap = LinearSegmentedColormap.from_list("tmp", [name, name])
    # cmap.set_under(config['plot']['params']["under_color"])
    # cmap.set_over(config['plot']['params']["over_color"])
    return cmap


class ColorMapper:

    def __init__(self,
                 data: sc.DataArray,
                 cmap: str = 'viridis',
                 masks_cmap: str = 'gray',
                 norm: str = "linear",
                 vmin=None,
                 vmax=None):
        # self._data = None
        self.cmap = _get_cmap(cmap)
        self.mask_cmap = _get_cmap(masks_cmap)
        self.user_vmin = vmin
        self.user_vmax = vmax
        self.vmin = np.inf
        self.vmax = np.NINF
        self.norm_flag = norm
        self.norm_func = None

    def rescale(self, data):
        """
        """
        vmin, vmax = fix_empty_range(find_limits(data, scale=self.norm_flag))
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

        self.norm_func.vmin = self.vmin
        self.norm_func.vmax = self.vmax

    # def _update_colors(self, data):
    #     # flat_values = self._maybe_repeat_values(self._data.data).flatten()
    #     self._rgba = self._cmap(self._norm_func(data.values))
    #     if data.masks:
    #         msk = next(iter(data.masks.values())).values
    #         self._rgba[msk] = self._mask_cmap(self._norm_func(data.values[msk]))
    #     # if len(self._data.masks) > 0:
    #     #     one_mask = self._maybe_repeat_values(
    #     #         sc.broadcast(reduce(lambda a, b: a | b, self._data.masks.values()),
    #     #                      dims=self._data.dims,
    #     #                      shape=self._data.shape)).flatten()
    #     #     rgba[one_mask] = self._mask_cmap(self._norm_func(flat_values[one_mask]))
    #     # self._mesh.set_facecolors(rgba)

    def rgba(self, data: sc.DataArray):
        """
        Update image array with new values.
        """
        # self._data = new_values
        # self._rescale_colormap(data=new_values)
        # self._update_colors(data=new_values)
        out = self.cmap(self.norm_func(data.values))
        if data.masks:
            msk = next(iter(data.masks.values())).values
            out[msk] = self.mask_cmap(self.norm_func(data.values[msk]))
        return out

    def set_norm(self, data):
        func = dict(linear=Normalize, log=LogNorm)[self.norm_flag]
        self.norm_func = func()
        self.rescale(data=data)
        # self._mesh.set_norm(self._norm_func)
        # self._set_clim()

    def toggle_norm(self):
        self.norm_flag = "log" if self.norm_flag == "linear" else "linear"
        self.vmin = np.inf
        self.vmax = np.NINF
        # self.set_norm(data=data)
        # self._set_mesh_colors()
        # self._ax.figure.canvas.draw_idle()
