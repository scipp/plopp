# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core.utils import number_to_variable, name_with_unit
# from ..core.view import View
from .basefig import BaseFig
from .canvas import Canvas
from .colormapper import ColorMapper
# from .io import fig_to_bytes
from .mesh import Mesh
from .line import Line

import matplotlib.pyplot as plt
import scipp as sc
from typing import Any, Tuple


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

        # self._children = {}
        # self.dims = {}
        self._scale = {} if scale is None else scale
        self._errorbars = errorbars
        self._mask_color = mask_color
        self._kwargs = kwargs

        self.canvas = Canvas(cbar=False, aspect=aspect, grid=grid)
        self.canvas.yscale = norm

        # for node in self.graph_nodes.values():
        #     new_values = node.request_data()
        #     self.update(new_values=new_values, key=node.id, draw=False)
        # self.canvas.autoscale(draw=False)  # self._children.values())
        # self.canvas.crop()
        # self.canvas.draw()

        self.render()
        self.canvas.autoscale()
        if crop is not None:
            # to_crop = {'dim': }

            self.canvas.crop(
                x={
                    **{
                        'dim': self.dims['x']['dim'],
                        'unit': self.dims['x']['unit']
                    },
                    **crop[self.dims['x']['dim']]
                })

    # def notify_view(self, message):
    #     node_id = message["node_id"]
    #     new_values = self.graph_nodes[node_id].request_data()
    #     self.update(new_values=new_values, key=node_id)

    # def autoscale(self, draw=False):
    #     self.canvas.autoscale(self._children.values())
    #     if draw:
    #         self.canvas.draw()

    def update(self, new_values: sc.DataArray, key: str, draw: bool = True):
        """
        Add new line or update line values.
        """
        if new_values.ndim != 1:
            raise ValueError("Figure1d can only be used to plot 1-D data.")

        if key not in self._children:

            line = Line(canvas=self.canvas,
                        data=new_values,
                        number=len(self._children),
                        **{
                            **{
                                'errorbars': self._errorbars,
                                'mask_color': self._mask_color
                            },
                            **self._kwargs
                        })
            self._children[key] = line
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
            # self.canvas.yscale = self._norm

            # if (self.dims['x']['dim'] in self._scale) and (
            #         self.canvas.xscale != self._scale[self.dims['x']['dim']]):
            #     self.canvas.xscale
            # if (self.dims['y']['dim'] in self._scale) and (
            #         self._ax.get_yscale() != self._scale[self.dims['y']['dim']]):
            #     self.logy()
            # if not self._ax.get_title():
            #     self._ax.set_title(new_values.name)

        else:
            self._children[key].update(new_values=new_values)

        if draw:
            self.canvas.autoscale()
            # self.canvas.draw()

    def crop(self, *args, **kwargs):
        self.canvas.crop(*args, **kwargs)
