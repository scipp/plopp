# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core.utils import name_with_unit
from .basefig import BaseFig
from .canvas import Canvas
from .colormapper import ColorMapper
from .mesh import Mesh

import scipp as sc


class Figure2d(BaseFig):

    def __init__(self,
                 *nodes,
                 cmap: str = 'viridis',
                 mask_cmap: str = 'gray',
                 norm: str = 'linear',
                 vmin=None,
                 vmax=None,
                 scale=None,
                 aspect='auto',
                 grid=False,
                 crop=None,
                 cbar=True,
                 title=None,
                 **kwargs):

        super().__init__(*nodes)

        self._scale = {} if scale is None else scale
        self._kwargs = kwargs
        self.canvas = Canvas(cbar=cbar, aspect=aspect, grid=grid, title=title)
        self.colormapper = ColorMapper(cmap=cmap,
                                       mask_cmap=mask_cmap,
                                       norm=norm,
                                       vmin=vmin,
                                       vmax=vmax,
                                       cax=self.canvas.cax)

        self.render()
        self.canvas.autoscale()
        if crop is not None:
            self.crop(**crop)

    def update(self, new_values: sc.DataArray, key: str, draw: bool = True):
        """
        Add new image or update image array with new values.
        """
        if new_values.ndim != 2:
            raise ValueError("Figure2d can only be used to plot 2-D data.")

        self.colormapper.update(data=new_values, key=key)

        if key not in self.artists:

            mesh = Mesh(canvas=self.canvas, data=new_values, **self._kwargs)
            self.artists[key] = mesh
            self.colormapper[key] = mesh
            self.dims.update({
                "x": {
                    'dim': new_values.dims[1],
                    'unit': new_values.meta[new_values.dims[1]].unit
                },
                "y": {
                    'dim': new_values.dims[0],
                    'unit': new_values.meta[new_values.dims[0]].unit
                }
            })

            self.canvas.xlabel = name_with_unit(
                var=new_values.meta[self.dims['x']['dim']])
            self.canvas.ylabel = name_with_unit(
                var=new_values.meta[self.dims['y']['dim']])
            if self.dims['x']['dim'] in self._scale:
                self.canvas.xscale = self._scale[self.dims['x']['dim']]
            if self.dims['y']['dim'] in self._scale:
                self.canvas.yscale = self._scale[self.dims['y']['dim']]

        self.artists[key].update(new_values=new_values)
        self.artists[key].set_colors(self.colormapper.rgba(self.artists[key].data))

        if draw:
            self.canvas.draw()

    def toggle_norm(self):
        self.colormapper.toggle_norm()
        self.canvas.draw()

    def crop(self, **limits):
        self.canvas.crop(
            **{
                xy: {
                    **{
                        'dim': self.dims[xy]['dim'],
                        'unit': self.dims[xy]['unit']
                    },
                    **limits[self.dims[xy]['dim']]
                }
                for xy in 'xy'
            })
