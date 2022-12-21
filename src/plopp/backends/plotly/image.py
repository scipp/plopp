# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ...core.utils import coord_as_bin_edges, repeat, merge_masks
from .canvas import Canvas

import numpy as np
import scipp as sc
import plotly.graph_objects as go
from PIL import Image

# def _find_dim_of_2d_coord(coords):
#     for xy, coord in coords.items():
#         if coord['var'].ndim == 2:
#             return (xy, coord['dim'])

# def _get_dims_of_1d_and_2d_coords(coords):
#     dim_2d = _find_dim_of_2d_coord(coords)
#     if dim_2d is None:
#         return None, None
#     axis_1d = 'xy'.replace(dim_2d[0], '')
#     dim_1d = (axis_1d, coords[axis_1d]['dim'])
#     return dim_1d, dim_2d

# def _maybe_repeat_values(data, dim_1d, dim_2d):
#     if dim_2d is None:
#         return data
#     return repeat(data, dim=dim_1d[1], n=2)[dim_1d[1], :-1]

# # def _from_data_array_to_heatmap(data):

#     dims = data.dims
#     x = coord_as_bin_edges(data, dims[1])
#     y = coord_as_bin_edges(data, dims[0])
#     z = data.data
#     xmin = x.values[0]
#     xmax = x.values[1]
#     ymin = y.values[0]
#     ymax = y.values[1]
#     zmin = z.min().value
#     zmax = z.max().value
#     return ([xmin, 0.5 * (xmin + xmax), xmax], [ymin, 0.5 * (ymin + ymax),
#                                                 ymax], [[zmin, zmin], [zmax, zmax]])


class Mesh:
    """
    Artist to represent two-dimensional data.

    Parameters
    ----------
    canvas:
        The canvas that will display the line.
    data:
        The initial data to create the line from.
    shading:
        The shading to use for the ``pcolormesh``.
    rasterized:
        Rasterize the mesh/image if ``True``.
    **kwargs:
        Additional arguments are forwarded to Matplotlib's ``pcolormesh``.
    """

    def __init__(self,
                 canvas: Canvas,
                 data: sc.DataArray,
                 shading: str = 'auto',
                 rasterized: bool = True,
                 **kwargs):

        # self._ax = canvas.ax
        self._fig = canvas.fig
        self._data = data
        # # If the grid is visible on the axes, we need to set that on again after we
        # # call pcolormesh, because that turns the grid off automatically.
        # # See https://github.com/matplotlib/matplotlib/issues/15600.
        # need_grid = self._ax.xaxis.get_gridlines()[0].get_visible()

        # to_dim_search = {}
        # string_labels = {}
        # bin_edge_coords = {}
        # for i, k in enumerate('yx'):
        #     to_dim_search[k] = {
        #         'dim': self._data.dims[i],
        #         'var': self._data.meta[self._data.dims[i]]
        #     }
        #     bin_edge_coords[k] = coord_as_bin_edges(self._data, self._data.dims[i])
        #     if self._data.meta[self._data.dims[i]].dtype == str:
        #         string_labels[k] = self._data.meta[self._data.dims[i]]

        # self._dim_1d, self._dim_2d = _get_dims_of_1d_and_2d_coords(to_dim_search)
        # self._mesh = None

        # x, y, z = _from_data_array_to_pcolormesh(data=self._data.data,
        #                                          coords=bin_edge_coords,
        #                                          dim_1d=self._dim_1d,
        #                                          dim_2d=self._dim_2d)
        # self.x, self.y, z = _from_data_array_to_heatmap(self._data)
        dims = self._data.dims
        self.x = coord_as_bin_edges(self._data, dims[1])
        self.y = coord_as_bin_edges(self._data, dims[0])
        z = self._data.data
        # xmin = self.x.values[0]
        # xmax = self.x.values[1]
        # ymin = self.y.values[0]
        # ymax = self.y.values[1]
        # zmin = z.min().value
        # zmax = z.max().value
        self._mesh = go.Heatmap(x=self.x.values,
                                y=self.y.values,
                                z=z.values,
                                showscale=False,
                                opacity=1)

        # self._mesh = go.Scatter(
        #     x=[self.x.values[0], self.x.values[-1]],
        #     y=[self.y.values[0], self.y.values[-1]],
        #     # z=z.values,
        #     # showscale=False,
        #     opacity=0)

        self._fig.add_trace(self._mesh)
        self._mesh = self._fig.data[-1]
        self._image = None

        layout = self._fig.layout
        self._layout_height = layout.height - layout.margin.b - layout.margin.t
        self._layout_width = layout.width - layout.margin.l - layout.margin.r
        # self._mesh.set_array(None)

        # for xy, var in string_labels.items():
        #     getattr(self._ax, f'set_{xy}ticks')(np.arange(float(var.shape[0])))
        #     getattr(self._ax, f'set_{xy}ticklabels')(var.values)

        # if need_grid:
        #     self._ax.grid(True)

    @property
    def data(self):
        """
        Get the Mesh's data in a form that may have been tweaked, compared to the
        original data, in the case of a two-dimensional coordinate.
        """
        return self._data
        # out = sc.DataArray(data=_maybe_repeat_values(
        #     data=self._data.data, dim_1d=self._dim_1d, dim_2d=self._dim_2d))
        # if self._data.masks:
        #     out.masks['one_mask'] = _maybe_repeat_values(data=sc.broadcast(
        #         merge_masks(self._data.masks),
        #         dims=self._data.dims,
        #         shape=self._data.shape),
        #                                                  dim_1d=self._dim_1d,
        #                                                  dim_2d=self._dim_2d)
        # return out

    def set_colors(self, rgba: np.ndarray):
        """
        Set the mesh's rgba colors:

        Parameters
        ----------
        rgba:
            The array of rgba colors.
        """
        return
        img = Image.fromarray(np.flipud(np.uint8(rgba * 255))).resize(
            (self._layout_width, self._layout_height), 0)

        if self._image is None:
            self._fig.update_layout(images=[
                go.layout.Image(x=self.x[0].value,
                                sizex=(self.x[-1] - self.x[0]).value,
                                y=self.y[-1].value,
                                sizey=(self.y[-1] - self.y[0]).value,
                                xref='x',
                                yref='y',
                                opacity=1.0,
                                layer='above',
                                sizing='stretch',
                                source=img)
            ])
            # self._fig.update_yaxes(scaleanchor="x")
            self._image = self._fig.layout['images'][-1]
        else:
            self._image.source = img
        # return
        # self._mesh.set_facecolors(rgba.reshape(np.prod(rgba.shape[:-1]), 4))

    def update(self, new_values: sc.DataArray):
        """
        Update image array with new values.

        Parameters
        ----------
        new_values:
            New data to update the mesh values from.
        """
        self._data = new_values
        # x, y, z = _from_data_array_to_heatmap(self._data)
        # self._mesh.z = self._data.values
        # self._fig.data[0].z = new_values.values
