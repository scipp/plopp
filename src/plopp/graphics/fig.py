# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core.utils import number_to_variable, name_with_unit
from ..core import View
from .utils import fig_to_bytes, silent_mpl_figure
from .mesh import Mesh
from .line import Line

import matplotlib.pyplot as plt
import scipp as sc
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
        self._errorbars = errorbars
        self._mask_color = mask_color
        self._kwargs = kwargs
        self._dims = {}
        self._children = {}

        if self._ax is None:
            if figsize is None:
                figsize = (6, 4)
            with silent_mpl_figure():
                self._fig, self._ax = plt.subplots(1, 1, figsize=figsize, dpi=96)
            self._fig.tight_layout(rect=[0.05, 0.02, 1.0, 1.0])
        else:
            self._fig = self._ax.get_figure()

        self._ax.set_aspect(aspect)
        self._ax.set_title(title)
        self._ax.grid(grid)
        self._legend = 0
        self._new_artist = False

        self._post_init()
        self.render()

    def _post_init(self):
        return

    def _to_image(self):
        from ipywidgets import Image
        width, height = self._fig.get_size_inches()
        dpi = self._fig.get_dpi()
        return Image(value=fig_to_bytes(self._fig),
                     width=width * dpi,
                     height=height * dpi,
                     format='png')

    def _autoscale(self):
        xmin = None
        xmax = None
        ymin = None
        ymax = None
        xscale = self._ax.get_xscale()
        yscale = self._ax.get_yscale()
        for child in self._children.values():
            xlims, ylims = child.get_limits(xscale=xscale, yscale=yscale)
            if isinstance(child, Line):
                if self._user_vmin is not None:
                    ylims[0] = self._user_vmin
                if self._user_vmax is not None:
                    ylims[1] = self._user_vmax
            if xmin is None or xlims[0].value < xmin:
                xmin = xlims[0].value
            if xmax is None or xlims[1].value > xmax:
                xmax = xlims[1].value
            if ymin is None or ylims[0].value < ymin:
                ymin = ylims[0].value
            if ymax is None or ylims[1].value > ymax:
                ymax = ylims[1].value
        self._ax.set_xlim(xmin, xmax)
        self._ax.set_ylim(ymin, ymax)

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
        new_values = self.graph_nodes[node_id].request_data()
        self.update(new_values=new_values, key=node_id)

    def update(self, new_values: sc.DataArray, key: str, draw: bool = True):
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
                if not self._ax.get_title():
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
                        sc.to_unit(number_to_variable(lims[m]),
                                   unit=self._dims[xy]['unit']).value
                        for m in ('min', 'max') if m in lims
                    ])

    def render(self):
        for node in self.graph_nodes.values():
            new_values = node.request_data()
            self.update(new_values=new_values, key=node.id, draw=False)
        self._autoscale()
        self.crop(**self._crop)
        self.draw()
