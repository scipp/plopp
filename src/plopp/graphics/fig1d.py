# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core.utils import name_with_unit
from .basefig import BaseFig
from .canvas import Canvas
from .line import Line

import scipp as sc


class Figure1d(BaseFig):

    def __init__(self,
                 *nodes,
                 norm: str = 'linear',
                 vmin=None,
                 vmax=None,
                 scale=None,
                 errorbars=True,
                 mask_color='black',
                 aspect='auto',
                 grid=False,
                 crop=None,
                 title=None,
                 **kwargs):

        super().__init__(*nodes)

        self._scale = {} if scale is None else scale
        self._errorbars = errorbars
        self._mask_color = mask_color
        self._kwargs = kwargs
        self.canvas = Canvas(cbar=False, aspect=aspect, grid=grid)
        self.canvas.yscale = norm

        self.render()
        self.canvas.autoscale()
        if crop is not None:
            self.crop(**crop)

    def update(self, new_values: sc.DataArray, key: str, draw: bool = True):
        """
        Add new line or update line values.
        """
        if new_values.ndim != 1:
            raise ValueError("Figure1d can only be used to plot 1-D data.")

        if key not in self.artists:

            line = Line(canvas=self.canvas,
                        data=new_values,
                        number=len(self.artists),
                        errorbars=self._errorbars,
                        mask_color=self._mask_color,
                        **self._kwargs)
            self.artists[key] = line
            if line.label:
                self.canvas.legend()

            self.dims['x'] = {
                'dim': new_values.dim,
                'unit': new_values.meta[new_values.dim].unit
            }

            self.canvas.xlabel = name_with_unit(
                var=new_values.meta[self.dims['x']['dim']])
            self.canvas.ylabel = name_with_unit(var=new_values.data, name="")

            if self.dims['x']['dim'] in self._scale:
                self.canvas.xscale = self._scale[self.dims['x']['dim']]

        else:
            self.artists[key].update(new_values=new_values)

        if draw:
            self.canvas.autoscale()

    def crop(self, **limits):
        self.canvas.crop(
            x={
                'dim': self.dims['x']['dim'],
                'unit': self.dims['x']['unit'],
                **limits[self.dims['x']['dim']]
            })
