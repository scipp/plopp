# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .tools import number_to_variable, name_with_unit
from .mesh import Mesh
from .line import Line
from .view import View

import matplotlib.pyplot as plt
from scipp import DataArray, to_unit
from typing import Any, Tuple


class Figure(View):

    def __init__(self,
                 *nodes,
                 ax: Any = None,
                 figsize: Tuple[float, ...] = None,
                 title: str = None,
                 grid: bool = False,
                 vmin=None,
                 vmax=None,
                 norm='linear',
                 aspect='auto',
                 scale=None,
                 cbar=True,
                 errorbars=True,
                 mask_color='black',
                 crop=None,
                 **kwargs):

        super().__init__(*nodes)

        self._fig = None
        self._ax = ax
        self._user_vmin = vmin
        self._user_vmax = vmax
        self._norm = norm
        self._scale = {} if scale is None else scale
        self._crop = {} if crop is None else crop
        self._cbar = cbar
        self._title = title
        self._errorbars = errorbars
        self._mask_color = mask_color
        self._kwargs = kwargs
        self._dims = {}
        self._children = {}

        if self._ax is None:
            if figsize is None:
                figsize = (6, 4)
            self._fig, self._ax = plt.subplots(1, 1, figsize=figsize
                                               # , dpi=200
                                               )
            self._fig.tight_layout(rect=[0.05, 0.02, 1.0, 1.0])
        else:
            self._fig = self._ax.get_figure()

        self._ax.set_aspect(aspect)
        self._ax.grid(grid)
        self._legend = 0
        self._new_artist = False

        self._post_init()
        self.render()

    def _post_init(self):
        return

    def _autoscale(self):
        global_xmin = None
        global_xmax = None
        global_ymin = None
        global_ymax = None
        xscale = self._ax.get_xscale()
        yscale = self._ax.get_yscale()
        for child in self._children.values():
            xmin, xmax, ymin, ymax = child.get_limits(xscale=xscale, yscale=yscale)
            if isinstance(child, Line):
                if self._user_vmin is not None:
                    ymin = self._user_vmin
                if self._user_vmax is not None:
                    ymax = self._user_vmax
            if global_xmin is None or xmin.value < global_xmin:
                global_xmin = xmin.value
            if global_xmax is None or xmax.value > global_xmax:
                global_xmax = xmax.value
            if global_ymin is None or ymin.value < global_ymin:
                global_ymin = ymin.value
            if global_ymax is None or ymax.value > global_ymax:
                global_ymax = ymax.value
        self._ax.set_xlim(global_xmin, global_xmax)
        self._ax.set_ylim(global_ymin, global_ymax)

    def draw(self):
        self._fig.canvas.draw_idle()

    def logx(self):
        swap_scales = {"linear": "log", "log": "linear"}
        self._ax.set_xscale(swap_scales[self._ax.get_xscale()])
        self._autoscale()
        self.draw()

    def logy(self):
        swap_scales = {"linear": "log", "log": "linear"}
        self._ax.set_yscale(swap_scales[self._ax.get_yscale()])
        self._autoscale()
        self.draw()

    def savefig(self, filename: str = None):
        """
        Save plot to file.
        Possible file extensions are `.jpg`, `.png` and `.pdf`.
        The default directory for writing the file is the same as the
        directory where the script or notebook is running.
        """
        self._fig.savefig(filename, bbox_inches="tight")

    def show(self):
        self._fig.show()

    def notify_view(self, message):
        node_id = message["node_id"]
        new_values = self._graph_nodes[node_id].request_data()
        self._update(new_values=new_values, key=node_id)

    def _update(self, new_values: DataArray, key: str, draw: bool = True):
        """
        Update image array with new values.
        """
        if new_values.ndim > 2:
            raise ValueError("Figure can only be used to plot 1-D and 2-D data.")
        if key not in self._children:
            self._new_artist = True
            if new_values.ndim == 1:
                line = Line(ax=self._ax,
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
                    self._ax.legend()
                self._dims['x'] = {
                    'dim': new_values.dim,
                    'unit': new_values.meta[new_values.dim].unit
                }
                self._ax.set_ylabel(name_with_unit(var=new_values.data, name=""))
                if self._ax.get_yscale() != self._norm:
                    self.logy()

            elif new_values.ndim == 2:
                self._children[key] = Mesh(ax=self._ax,
                                           data=new_values,
                                           vmin=self._user_vmin,
                                           vmax=self._user_vmax,
                                           norm=self._norm,
                                           crop=self._crop,
                                           **{
                                               **{
                                                   'cbar': self._cbar,
                                               },
                                               **self._kwargs
                                           })
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
                if (self._dims['y']['dim'] in self._scale) and (
                        self._ax.get_yscale() != self._scale[self._dims['y']['dim']]):
                    self.logy()
                self._ax.set_ylabel(
                    name_with_unit(var=new_values.meta[self._dims['y']['dim']]))
                if self._title is None:
                    self._ax.set_title(new_values.name)

            self._ax.set_xlabel(
                name_with_unit(var=new_values.meta[self._dims['x']['dim']]))
            if (self._dims['x']['dim'] in self._scale) and (
                    self._ax.get_xscale() != self._scale[self._dims['x']['dim']]):
                self.logx()

        else:
            self._children[key].update(new_values=new_values)

        if draw:
            self.draw()

    def crop(self, **kwargs):
        for dim, lims in kwargs.items():
            for xy in self._dims:
                if dim == self._dims[xy]['dim']:
                    getattr(self._ax, f'set_{xy}lim')(*[
                        to_unit(number_to_variable(lims[m]),
                                unit=self._dims[xy]['unit']).value
                        for m in ('min', 'max') if m in lims
                    ])

    def render(self):
        for node in self._graph_nodes.values():
            new_values = node.request_data()
            self._update(new_values=new_values, key=node.id, draw=False)
        self._autoscale()
        self.crop(**self._crop)
        self.draw()
