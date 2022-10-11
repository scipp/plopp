# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core.utils import number_to_variable, name_with_unit
from .fig import Figure
from .color_mapper import ColorMapper
from .io import fig_to_bytes
from .mesh import Mesh
from .line import Line

import matplotlib.pyplot as plt
import scipp as sc
from typing import Any, Tuple


class Figure2d(Figure):

    def __init__(self,
                 *args,
                 cmap: str = 'viridis',
                 mask_cmap: str = 'gray',
                 norm: str = 'linear',
                 vmin=None,
                 vmax=None,
                 **kwargs):

        self.colormapper = ColorMapper(cmap=cmap,
                                       mask_cmap=mask_cmap,
                                       norm=norm,
                                       vmin=vmin,
                                       vmax=vmax)

        super().__init__(*args, **kwargs)

    def update(self, new_values: sc.DataArray, key: str, draw: bool = True):
        """
        Update image array with new values.
        """
        if new_values.ndim != 2:
            raise ValueError("Figure can only be used to plot 2-D data.")

        self.colormapper.update(data=new_values)

        if key not in self._children:

            # self.colormapper.autoscale(data=new_values)
            mesh = Mesh(ax=self._ax,
                        data=new_values,
                        vmin=self._user_vmin,
                        vmax=self._user_vmax,
                        norm=self._norm,
                        **{
                            **{
                                'cbar': self._cbar,
                            },
                            **self._kwargs
                        })
            self._children[key] = mesh
            self.colormapper[key] = mesh
            self._dims.update({
                "x": {
                    'dim': new_values.dims[1],
                    'unit': new_values.meta[new_values.dims[1]].unit
                },
                "y": {
                    'dim': new_values.dims[0],
                    'unit': new_values.meta[new_values.dims[0]].unit
                }
            })

            self._ax.set_xlabel(
                name_with_unit(var=new_values.meta[self._dims['x']['dim']]))
            self._ax.set_ylabel(
                name_with_unit(var=new_values.meta[self._dims['y']['dim']]))
            if (self._dims['x']['dim'] in self._scale) and (
                    self._ax.get_xscale() != self._scale[self._dims['x']['dim']]):
                self.logx()
            if (self._dims['y']['dim'] in self._scale) and (
                    self._ax.get_yscale() != self._scale[self._dims['y']['dim']]):
                self.logy()
            if not self._ax.get_title():
                self._ax.set_title(new_values.name)

        # else:
        self._children[key].update(new_values=new_values)
        self._children[key].set_colors(self.colormapper.rgba(self._children[key].data))

        if draw:
            self.draw()