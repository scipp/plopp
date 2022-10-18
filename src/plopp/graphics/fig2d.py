# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core.utils import name_with_unit
from .basefig import BaseFig
from .canvas import Canvas
from .colormapper import ColorMapper
# from .io import fig_to_bytes
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
                 **kwargs):

        super().__init__(*nodes)

        # print('start of fig init', nodes)
        # self._children = {}
        # self.dims = {}
        self._scale = {} if scale is None else scale
        self.canvas = Canvas(cbar=True, aspect=aspect, grid=grid)
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

        # for node in self.graph_nodes.values():
        #     new_values = node.request_data()
        #     self.update(new_values=new_values, key=node.id, draw=False)
        # self.canvas.autoscale()  # self._children.values())
        # self.crop(**self._crop)
        # self.canvas.draw()
        # print('end of fig init', self.colormapper.children)

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
        Add new image or update image array with new values.
        """
        if new_values.ndim != 2:
            raise ValueError("Figure2d can only be used to plot 2-D data.")

        self.colormapper.update(data=new_values)

        if key not in self._children:

            # self.colormapper.autoscale(data=new_values)
            mesh = Mesh(
                canvas=self.canvas,
                data=new_values
                # vmin=self._user_vmin,
                # vmax=self._user_vmax,
                # norm=self._norm,
                # **{
                #     **{
                #         'cbar': self._cbar,
                #     },
                #     **self._kwargs
                # }
            )
            self._children[key] = mesh
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

            # if (self.dims['x']['dim'] in self._scale) and (
            #         self.canvas.xscale != self._scale[self.dims['x']['dim']]):
            #     self.canvas.xscale
            # if (self.dims['y']['dim'] in self._scale) and (
            #         self._ax.get_yscale() != self._scale[self.dims['y']['dim']]):
            #     self.logy()
            # if not self._ax.get_title():
            #     self._ax.set_title(new_values.name)

        # else:
        self._children[key].update(new_values=new_values)
        self._children[key].set_colors(self.colormapper.rgba(self._children[key].data))

        # print('after update', self.colormapper.children)

        if draw:
            self.canvas.draw()

    def toggle_norm(self):
        # print('figure togglenorm', self.colormapper.children)
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
