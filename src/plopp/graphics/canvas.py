# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core.limits import find_limits, fix_empty_range
from ..core.utils import number_to_variable, name_with_unit
from ..core import View
from .io import fig_to_bytes
from .mesh import Mesh
from .line import Line

from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
import scipp as sc
from typing import Any, Tuple


def _none_if_not_finite(x):
    return x if np.isfinite(x) else None


class Canvas:

    def __init__(
            self,
            # *nodes,
            ax: Any = None,
            figsize: Tuple[float, ...] = None,
            title: str = None,
            grid: bool = False,
            vmin=None,
            vmax=None,
            norm='linear',
            aspect='auto',
            scale=None,
            cbar=False,
            crop=None,
            **kwargs):

        # super().__init__(*nodes)

        self.fig = None
        self.ax = ax
        self._user_vmin = vmin
        self._user_vmax = vmax
        self._norm = norm
        self._scale = {} if scale is None else scale
        self._crop = {} if crop is None else crop
        # self._cbar = cbar
        # self._errorbars = errorbars
        # self._mask_color = mask_color
        self._kwargs = kwargs
        # self._dims = {}
        # self._children = {}

        if self.ax is None:
            if figsize is None:
                figsize = (6, 4)
            # self.fig, self.ax = plt.subplots(1, 1, figsize=figsize, dpi=96)
            # self.fig.tight_layout(rect=[0.05, 0.02, 1.0, 1.0])
            self.fig = plt.figure(figsize=figsize, dpi=96)
            left = 0.11
            right = 0.9
            bottom = 0.11
            top = 0.95
            if cbar:
                cbar_width = 0.03
                cbar_gap = 0.04
                self.ax = self.fig.add_axes(
                    [left, bottom, right - left - cbar_width - cbar_gap, top - bottom])
                self.cax = self.fig.add_axes(
                    [right - cbar_width, bottom, cbar_width, top - bottom])
            else:
                self.ax = self.fig.add_axes([left, bottom, right - left, top - bottom])
                self.cax = None
            # self.fig.tight_layout()
            # cax = fig.add_axes([0.27, 0.8, 0.5, 0.05])
        else:
            self.fig = self.ax.get_figure()

        self.ax.set_aspect(aspect)
        self.ax.set_title(title)
        self.ax.grid(grid)
        self._legend = 0

        self._xmin = np.inf
        self._xmax = np.NINF
        self._ymin = np.inf
        self._ymax = np.NINF
        # self._new_artist = False

        # self._post_init()
        # self.render()

    # def _post_init(self):
    #     return

    def _to_image(self):
        from ipywidgets import Image
        width, height = self.fig.get_size_inches()
        dpi = self.fig.get_dpi()
        return Image(value=fig_to_bytes(self.fig),
                     width=width * dpi,
                     height=height * dpi,
                     format='png')

    def autoscale(self, draw=True):
        """
        Matplotlib's autoscale only takes lines into account. We require a special
        handline for meshes, which is part of the axes collections.
        """
        if self.ax.lines:
            self.ax.relim()
            self.ax.autoscale()
            xmin, xmax = self.ax.get_xlim()
            ymin, ymax = self.ax.get_ylim()
            self._xmin = min(self._xmin, xmin)
            self._xmax = max(self._xmax, xmax)
            self._ymin = min(self._ymin, ymin)
            self._ymax = max(self._ymax, ymax)
        for c in self.ax.collections:
            coords = c.get_coordinates()
            left, right = fix_empty_range(
                find_limits(sc.array(dims=['x', 'y'], values=coords[..., 0]),
                            scale=self.xscale))
            bottom, top = fix_empty_range(
                find_limits(sc.array(dims=['x', 'y'], values=coords[..., 1]),
                            scale=self.yscale))
            self._xmin = min(self._xmin, left.value)
            self._xmax = max(self._xmax, right.value)
            self._ymin = min(self._ymin, bottom.value)
            self._ymax = max(self._ymax, top.value)
        self.ax.set_xlim(_none_if_not_finite(self._xmin),
                         _none_if_not_finite(self._xmax))
        self.ax.set_ylim(_none_if_not_finite(self._ymin),
                         _none_if_not_finite(self._ymax))
        if draw:
            self.draw()

    def draw(self):
        self.fig.canvas.draw_idle()

    def savefig(self, filename: str = None):
        """
        Save plot to file.
        Possible file extensions are `.jpg`, `.png` and `.pdf`.
        The default directory for writing the file is the same as the
        directory where the script or notebook is running.
        """
        self.fig.savefig(filename, bbox_inches="tight")

    def show(self):
        self.fig.show()

    def notify_view(self, message):
        node_id = message["node_id"]
        new_values = self.graph_nodes[node_id].request_data()
        self.update(new_values=new_values, key=node_id)

    # def update(self, new_values: sc.DataArray, key: str, draw: bool = True):
    #     """
    #     Update image array with new values.
    #     """
    #     if new_values.ndim > 2:
    #         raise ValueError("Figure can only be used to plot 1-D and 2-D data.")
    #     if key not in self._children:
    #         self._new_artist = True
    #         if new_values.ndim == 1:
    #             line = Line(ax=self.ax,
    #                         data=new_values,
    #                         number=len(self._children),
    #                         **{
    #                             **{
    #                                 'errorbars': self._errorbars,
    #                                 'mask_color': self._mask_color
    #                             },
    #                             **self._kwargs
    #                         })
    #             self._children[key] = line
    #             if line.label:
    #                 self.ax.legend()
    #             self._dims['x'] = {
    #                 'dim': new_values.dim,
    #                 'unit': new_values.meta[new_values.dim].unit
    #             }
    #             self.ax.set_ylabel(name_with_unit(var=new_values.data, name=""))
    #             if self.ax.get_yscale() != self._norm:
    #                 self.logy()

    #         elif new_values.ndim == 2:
    #             self._children[key] = Mesh(ax=self.ax,
    #                                        data=new_values,
    #                                        vmin=self._user_vmin,
    #                                        vmax=self._user_vmax,
    #                                        norm=self._norm,
    #                                        **{
    #                                            **{
    #                                                'cbar': self._cbar,
    #                                            },
    #                                            **self._kwargs
    #                                        })
    #             self._dims.update({
    #                 "x": {
    #                     'dim': new_values.dims[1],
    #                     'unit': new_values.meta[new_values.dims[1]].unit
    #                 },
    #                 "y": {
    #                     'dim': new_values.dims[0],
    #                     'unit': new_values.meta[new_values.dims[0]].unit
    #                 }
    #             })
    #             if (self._dims['y']['dim'] in self._scale) and (
    #                     self.ax.get_yscale() != self._scale[self._dims['y']['dim']]):
    #                 self.logy()
    #             self.ax.set_ylabel(
    #                 name_with_unit(var=new_values.meta[self._dims['y']['dim']]))
    #             if not self.ax.get_title():
    #                 self.ax.set_title(new_values.name)

    #         self.ax.set_xlabel(
    #             name_with_unit(var=new_values.meta[self._dims['x']['dim']]))
    #         if (self._dims['x']['dim'] in self._scale) and (
    #                 self.ax.get_xscale() != self._scale[self._dims['x']['dim']]):
    #             self.logx()

    #     else:
    #         self._children[key].update(new_values=new_values)

    #     if draw:
    #         self.draw()

    def crop(self, limits=None):
        if limits is None:
            limits = self._crop
        for dim, lims in limits.items():
            for xy in self._dims:
                if dim == self._dims[xy]['dim']:
                    getattr(self.ax, f'set_{xy}lim')(*[
                        sc.to_unit(number_to_variable(lims[m]),
                                   unit=self._dims[xy]['unit']).value
                        for m in ('min', 'max') if m in lims
                    ])

    # def render(self):
    #     for node in self.graph_nodes.values():
    #         new_values = node.request_data()
    #         self.update(new_values=new_values, key=node.id, draw=False)
    #     self._autoscale()
    #     self.crop(**self._crop)
    #     self.draw()

    def to_bytes(self, form='png'):
        """
        Convert a Matplotlib figure to png (default) or svg bytes.
        """
        buf = BytesIO()
        self.fig.savefig(buf, format=form, bbox_inches='tight')
        buf.seek(0)
        return buf.getvalue()

    def legend(self):
        self.ax.legend()

    @property
    def xlabel(self):
        return self.ax.get_xlabel()

    @xlabel.setter
    def xlabel(self, lab):
        self.ax.set_xlabel(lab)

    @property
    def ylabel(self):
        return self.ax.get_ylabel()

    @ylabel.setter
    def ylabel(self, lab):
        self.ax.set_ylabel(lab)

    @property
    def xscale(self):
        return self.ax.get_xscale()

    @xscale.setter
    def xscale(self, scale):
        self.ax.set_xscale(scale)
        # self.autoscale()

    @property
    def yscale(self):
        return self.ax.get_yscale()

    @yscale.setter
    def yscale(self, scale):
        self.ax.set_yscale(scale)
        # self.autoscale()

    def reset_mode(self):
        self.fig.canvas.toolbar.mode = ''

    def zoom(self):
        self.fig.canvas.toolbar.zoom()

    def pan(self):
        self.fig.canvas.toolbar.pan()

    def save(self):
        self.fig.canvas.toolbar.save_figure()

    def logx(self):
        # swap_scales = {"linear": "log", "log": "linear"}
        self.xscale = 'log' if self.xscale == 'linear' else 'linear'
        self._xmin = np.inf
        self._xmax = np.NINF
        self.autoscale()
        # self.draw()

    def logy(self):
        # swap_scales = {"linear": "log", "log": "linear"}
        self.yscale = 'log' if self.yscale == 'linear' else 'linear'
        self._ymin = np.inf
        self._ymax = np.NINF
        self.autoscale()
        # self.draw()

    # def logy(self):
    #     swap_scales = {"linear": "log", "log": "linear"}
    #     self.ax.set_yscale(swap_scales[self.ax.get_yscale()])
    #     self._autoscale()
    #     self.draw()