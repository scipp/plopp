# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .displayable import Displayable
from .axes import Axes
from .io import fig_to_pngbytes
from .tools import number_to_variable, name_with_unit
from .toolbar import Toolbar
from .mesh import Mesh
from .line import Line
from .view import View

from io import BytesIO
import ipywidgets as ipw
import matplotlib.pyplot as plt
from scipp import DataArray, to_unit
from typing import Any, Tuple


class SideBar(list, Displayable):

    def to_widget(self):
        return ipw.VBox([child.to_widget() for child in self])


class FigureInteractive(Axes):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # self._fig = None
        # self._ax = ax
        # self._user_vmin = vmin
        # self._user_vmax = vmax
        # self._norm = norm
        # self._scale = {} if scale is None else scale
        # self._crop = {} if crop is None else crop
        # self._cbar = cbar
        # self._title = title
        # self._errorbars = errorbars
        # self._mask_color = mask_color
        # self._kwargs = kwargs
        # self._dims = {}
        # self._children = {}

        # # cfg = config['plot']
        # if self._ax is None:
        #     # dpi = 300
        #     if figsize is None:
        #         figsize = (6, 4)
        #     #     figsize = (2000 / dpi, 1400 / dpi)
        #     self._fig, self._ax = plt.subplots(1, 1, figsize=figsize
        #                                        # , dpi=200
        #                                        )
        #     # self._fig, self._ax = plt.subplots(1, 1, figsize=figsize)
        #     self._fig.tight_layout(rect=[0.05, 0.02, 1.0, 1.0])
        #     if self._uses_widget_backend:
        #         # self._fig.set_dpi(200)
        #         # self._fig.canvas.layout.width = '6in'
        #         # self._fig.canvas.layout.height = '4in'
        #     # else:
        #     #     # self._fig.tight_layout(rect=[0.05, 0.02, 1.0, 1.0])
        #     #     self._fig.set_size_inches(6, 4)
        # else:
        #     self._fig = self._ax.get_figure()

        self._fig.canvas.toolbar_visible = False
        self._fig.canvas.header_visible = False

        self.left_bar = SideBar()
        self.right_bar = SideBar()
        self.bottom_bar = SideBar()
        self.top_bar = SideBar()

        self.toolbar = Toolbar(
            tools={
                'home': self.home,
                'pan': self.pan,
                'zoom': self.zoom,
                'logx': self.logx,
                'logy': self.logy,
                'save': self.save
            })
        self._fig.canvas.toolbar_visible = False
        self._fig.canvas.header_visible = False
        self.left_bar.append(self.toolbar)

        self.render()

    # if self._uses_widget_backend:

    #     from ipywidgets import Widget

    #     if hasattr(Widget, '_repr_mimebundle_'):

    #         def _repr_mimebundle_(self, include=None, exclude=None):
    #             """
    #             Mimebundle display representation for jupyter notebooks.
    #             """
    #             return self.to_widget()._repr_mimebundle_(include=include,
    #                                                       exclude=exclude)
    #             # if self._uses_widget_backend:
    #             #     return self.to_widget()._repr_mimebundle_()
    #             # else:
    #             #     # return {'text/plain': 'Figure', 'image/png': fig_to_pngbytes(self._fig)}
    #             #     return {
    #             #         'text/plain': 'Figure',
    #             #         'image/svg+xml': fig_to_pngbytes(self._fig, form='svg').decode()
    #             #     }
    #     else:

    #         def _ipython_display_(self):
    #             """
    #             IPython display representation for Jupyter notebooks.
    #             """
    #             return self.to_widget()._ipython_display_()

    # else:

    def _repr_mimebundle_(self, include=None, exclude=None):
        """
        Mimebundle display representation for jupyter notebooks.
        """
        return self.to_widget()._repr_mimebundle_(include=include, exclude=exclude)
        # # if self._uses_widget_backend:

        #     out = self.to_widget()
        #     if hasattr(out, '_repr_mimebundle_'):
        #         return out._repr_mimebundle_(include=include,
        #                                                   exclude=exclude)
        #     else:
        #         return
        # # else:
        # #     # return {'text/plain': 'Figure', 'image/png': fig_to_pngbytes(self._fig)}
        # #     return {
        # #         'text/plain': 'Figure',
        # #         'image/svg+xml': fig_to_pngbytes(self._fig, form='svg').decode()
        # #     }

    def to_widget(self) -> ipw.Widget:
        """
        Convert the Matplotlib figure to a widget. If the ipympl (widget)
        backend is in use, return the custom toolbar and the figure canvas.
        If not, convert the plot to a png image and place inside an ipywidgets
        Image container.
        """
        # if self._uses_widget_backend:
        canvas = self._fig.canvas
        # else:
        #     width, height = self._fig.get_size_inches()
        #     dpi = self._fig.get_dpi()
        #     canvas = ipw.Image(value=fig_to_pngbytes(self._fig),
        #                        width=width * dpi,
        #                        height=height * dpi)

        return ipw.VBox([
            self.top_bar.to_widget(),
            ipw.HBox([self.left_bar.to_widget(), canvas,
                      self.right_bar.to_widget()]),
            self.bottom_bar.to_widget()
        ])

    # def _autoscale(self):
    #     global_xmin = None
    #     global_xmax = None
    #     global_ymin = None
    #     global_ymax = None
    #     xscale = self._ax.get_xscale()
    #     yscale = self._ax.get_yscale()
    #     for child in self._children.values():
    #         xmin, xmax, ymin, ymax = child.get_limits(xscale=xscale, yscale=yscale)
    #         if isinstance(child, Line):
    #             if self._user_vmin is not None:
    #                 ymin = self._user_vmin
    #             if self._user_vmax is not None:
    #                 ymax = self._user_vmax
    #         if global_xmin is None or xmin.value < global_xmin:
    #             global_xmin = xmin.value
    #         if global_xmax is None or xmax.value > global_xmax:
    #             global_xmax = xmax.value
    #         if global_ymin is None or ymin.value < global_ymin:
    #             global_ymin = ymin.value
    #         if global_ymax is None or ymax.value > global_ymax:
    #             global_ymax = ymax.value
    #     self._ax.set_xlim(global_xmin, global_xmax)
    #     self._ax.set_ylim(global_ymin, global_ymax)

    # def draw(self):
    #     self._fig.canvas.draw_idle()

    def home(self):
        self._autoscale()
        self.crop(**self._crop)
        self.draw()

    def pan(self):
        if self._fig.canvas.toolbar.mode == "Zoom":
            self.toolbar.zoom()
        self._fig.canvas.toolbar.pan()

    def zoom(self):
        self._fig.canvas.toolbar.zoom()

    def save(self):
        self._fig.canvas.toolbar.save_figure()

    def logx(self):
        super().logx()
        self.toolbar.logx.value = self._ax.get_xscale() == 'log'
        # swap_scales = {"linear": "log", "log": "linear"}
        # self._ax.set_xscale(swap_scales[self._ax.get_xscale()])
        # self._autoscale()
        # self.draw()

    def logy(self):
        super().logy()
        self.toolbar.logy.value = self._ax.get_yscale() == 'log'
        # self.toolbar.logy(disconnect=True)
        # swap_scales = {"linear": "log", "log": "linear"}
        # self._ax.set_yscale(swap_scales[self._ax.get_yscale()])
        # self._autoscale()
        # self.draw()

    def savefig(self, filename: str = None):
        """
        Save plot to file.
        Possible file extensions are `.jpg`, `.png` and `.pdf`.
        The default directory for writing the file is the same as the
        directory where the script or notebook is running.
        """
        self._fig.savefig(filename, bbox_inches="tight")

    # def notify_view(self, message):
    #     node_id = message["node_id"]
    #     new_values = self._graph_nodes[node_id].request_data()
    #     self._update(new_values=new_values, key=node_id)

    # def _update(self, new_values: DataArray, key: str, draw: bool = True):
    #     """
    #     Update image array with new values.
    #     """
    #     if new_values.ndim > 2:
    #         raise ValueError("Figure can only be used to plot 1-D and 2-D data.")
    #     if key not in self._children:
    #         self._new_artist = True
    #         if new_values.ndim == 1:
    #             line = Line(ax=self._ax,
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
    #                 self._ax.legend()
    #             self._dims['x'] = {
    #                 'dim': new_values.dim,
    #                 'unit': new_values.meta[new_values.dim].unit
    #             }
    #             self._ax.set_ylabel(name_with_unit(var=new_values.data, name=""))
    #             # TODO: this is not great, involves implementation details of the
    #             # toolbar. However, setting the yscale of the axis manually would mean
    #             # we need to update the value of the 'logy' button depending on the
    #             # value of self._norm, and updating that value would trigger a callback
    #             # which would draw the axes a second time.
    #             self.toolbar.members['toggle_yaxis_scale'].value = self._norm == 'log'

    #         elif new_values.ndim == 2:
    #             self._children[key] = Mesh(ax=self._ax,
    #                                        data=new_values,
    #                                        vmin=self._user_vmin,
    #                                        vmax=self._user_vmax,
    #                                        norm=self._norm,
    #                                        crop=self._crop,
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
    #             if new_values.dims[0] in self._scale:
    #                 self.toolbar.members['toggle_yaxis_scale'].value = self._scale[
    #                     self._dims['y']['dim']] == 'log'
    #             self._ax.set_ylabel(
    #                 name_with_unit(var=new_values.meta[self._dims['y']['dim']]))
    #             if self._title is None:
    #                 self._ax.set_title(new_values.name)

    #         self._ax.set_xlabel(
    #             name_with_unit(var=new_values.meta[self._dims['x']['dim']]))
    #         if self._dims['x']['dim'] in self._scale:
    #             self.toolbar.members['toggle_xaxis_scale'].value = self._scale[
    #                 self._dims['x']['dim']] == 'log'

    #     else:
    #         self._children[key].update(new_values=new_values)

    #     if draw:
    #         self.draw()

    # def crop(self, **kwargs):
    #     for dim, lims in kwargs.items():
    #         for xy in self._dims:
    #             if dim == self._dims[xy]['dim']:
    #                 getattr(self._ax, f'set_{xy}lim')(*[
    #                     to_unit(number_to_variable(lims[m]),
    #                             unit=self._dims[xy]['unit']).value
    #                     for m in ('min', 'max') if m in lims
    #                 ])

    # def render(self):
    #     for node in self._graph_nodes.values():
    #         new_values = node.request_data()
    #         self._update(new_values=new_values, key=node.id, draw=False)
    #     self._autoscale()
    #     self.crop(**self._crop)
    #     self.draw()
