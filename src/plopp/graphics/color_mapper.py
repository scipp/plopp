# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core.limits import find_limits, fix_empty_range
from ..core.utils import merge_masks

from matplotlib.colors import Normalize, LogNorm, LinearSegmentedColormap
from matplotlib import cm
import scipp as sc
from copy import copy
import numpy as np


def _get_cmap(name, nan_color=None):

    try:
        cmap = copy(cm.get_cmap(name))
    except ValueError:
        cmap = LinearSegmentedColormap.from_list("tmp", [name, name])
    # cmap.set_under(config['plot']['params']["under_color"])
    # cmap.set_over(config['plot']['params']["over_color"])
    if nan_color is not None:
        cmap.set_bad(color=nan_color)
    return cmap


class ColorMapper:

    def __init__(self,
                 cmap: str = 'viridis',
                 mask_cmap: str = 'gray',
                 norm: str = "linear",
                 vmin=None,
                 vmax=None,
                 nan_color=None):
        self.cmap = _get_cmap(cmap, nan_color=nan_color)
        self.mask_cmap = _get_cmap(mask_cmap, nan_color=nan_color)
        self.user_vmin = vmin
        self.user_vmax = vmax
        self.vmin = np.inf
        self.vmax = np.NINF
        self.norm_flag = norm
        self.norm_func = None

    def rescale(self, data):
        """
        Re-compute the min and max range of values, given new values.
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

    def rgba(self, data: sc.DataArray):
        """
        Return rgba values given a data array.
        """
        out = self.cmap(self.norm_func(data.values))
        if data.masks:
            one_mask = merge_masks(data.masks).values
            out[one_mask] = self.mask_cmap(self.norm_func(data.values[one_mask]))
        return out

    def set_norm(self, data):
        """
        Set the norm of the color mapper and update the min/max values.
        """
        func = dict(linear=Normalize, log=LogNorm)[self.norm_flag]
        self.norm_func = func()
        self.rescale(data=data)

    def toggle_norm(self):
        """
        Toggle the norm flag, between `linear` and `log`.
        """
        self.norm_flag = "log" if self.norm_flag == "linear" else "linear"
        self.vmin = np.inf
        self.vmax = np.NINF
