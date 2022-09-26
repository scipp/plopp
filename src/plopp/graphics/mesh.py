# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core.limits import find_limits, fix_empty_range
from ..core.utils import coord_as_bin_edges, name_with_unit, repeat
from .color_mapper import ColorMapper

from functools import reduce
from matplotlib.colors import Normalize, LogNorm, LinearSegmentedColormap
from matplotlib.pyplot import colorbar
from matplotlib import cm
import numpy as np
import scipp as sc
from typing import Any

# def _get_cmap(name: str = 'viridis'):

#     try:
#         cmap = copy(cm.get_cmap(name))
#     except ValueError:
#         cmap = LinearSegmentedColormap.from_list("tmp", [name, name])

#     # cmap.set_under(config['plot']['params']["under_color"])
#     # cmap.set_over(config['plot']['params']["over_color"])
#     return cmap


def _find_dim_of_2d_coord(coords):
    for xy, coord in coords.items():
        if coord['var'].ndim == 2:
            return (xy, coord['dim'])


def _get_dims_of_1d_and_2d_coords(coords):
    dim_2d = _find_dim_of_2d_coord(coords)
    if dim_2d is None:
        return None, None
    axis_1d = 'xy'.replace(dim_2d[0], '')
    dim_1d = (axis_1d, coords[axis_1d]['dim'])
    return dim_1d, dim_2d


def _maybe_repeat_values(data, coords):
    dim_1d, dim_2d = _get_dims_of_1d_and_2d_coords(coords)
    if dim_2d is None:
        return data
    return repeat(data, dim=dim_1d[1], n=2)[dim_1d[1], :-1]


def _from_data_array_to_pcolormesh(data, coords):
    # xy = {k: coord_as_bin_edges(self._data, self._dims[k]) for k in 'xy'}
    z = _maybe_repeat_values(data=data, coords=coords)

    dim_1d, dim_2d = _get_dims_of_1d_and_2d_coords(coords)
    if dim_2d is None:
        return coords['x']['var'], coords['y']['var'], z

    # Broadcast 1d coord to 2d and repeat along 1d dim
    # TODO: It may be more efficient here to first repeat and then broadcast, but
    # the current order is simpler in implementation.
    broadcasted_coord = repeat(sc.broadcast(coords[dim_1d[0]]['var'],
                                            sizes={
                                                **coords[dim_2d[0]]['var'].sizes,
                                                **coords[dim_1d[0]]['var'].sizes
                                            }).transpose(data.dims),
                               dim=dim_1d[1],
                               n=2)

    # Repeat 2d coord along 1d dim
    repeated_coord = repeat(coords[dim_2d[0]]['var'].transpose(data.dims),
                            dim=dim_1d[1],
                            n=2)

    out = {dim_1d[0]: broadcasted_coord[dim_1d[1], 1:-1], dim_2d[0]: repeated_coord}

    return out['x'], out['y'], z


class Mesh:
    """
    Class for 2 dimensional plots.
    """

    def __init__(self,
                 ax,
                 data,
                 cax: Any = None,
                 cmap: str = None,
                 masks_cmap: str = "gray",
                 norm: str = "linear",
                 vmin=None,
                 vmax=None,
                 cbar=True,
                 **kwargs):

        self.color_mapper = ColorMapper(data=data,
                                        cmap=cmap,
                                        masks_cmap=masks_cmap,
                                        norm=norm,
                                        vmin=vmin,
                                        vmax=vmax)

        self._ax = ax
        self._data = data
        self._dims = {'x': self._data.dims[1], 'y': self._data.dims[0]}
        self._bin_edge_coords = {
            k: {
                'dim': self._dims[k],
                'var': coord_as_bin_edges(self._data, self._dims[k])
            }
            for k in 'xy'
        }

        self._xlabel = None
        self._ylabel = None
        self._title = None
        # self._user_vmin = vmin
        # self._user_vmax = vmax
        # self._vmin = np.inf
        # self._vmax = np.NINF

        # self._cmap = _get_cmap(cmap)
        self._cax = cax
        # self._mask_cmap = _get_cmap(masks_cmap)
        # self._norm_flag = norm
        # self._norm_func = None

        self._mesh = None
        self._cbar = cbar

        self._extend = "neither"
        if (vmin is not None) and (vmax is not None):
            self._extend = "both"
        elif vmin is not None:
            self._extend = "min"
        elif vmax is not None:
            self._extend = "max"

        self._make_mesh(**kwargs)

    # def _find_dim_of_2d_coord(self):
    #     for xy in 'xy':
    #         if self._data.meta[self._dims[xy]].ndim == 2:
    #             return (xy, self._dims[xy])

    # def _get_dims_of_1d_and_2d_coords(self):
    #     dim_2d = self._find_dim_of_2d_coord()
    #     if dim_2d is None:
    #         return None, None
    #     axis_1d = 'xy'.replace(dim_2d[0], '')
    #     dim_1d = (axis_1d, self._dims[axis_1d])
    #     return dim_1d, dim_2d

    # def _maybe_repeat_values(self, array):
    #     dim_1d, dim_2d = self._get_dims_of_1d_and_2d_coords()
    #     if dim_2d is None:
    #         return array.values
    #     return repeat(array, dim=dim_1d[1], n=2)[dim_1d[1], :-1].values

    # def _from_data_array_to_pcolormesh(self):
    #     xy = {k: coord_as_bin_edges(self._data, self._dims[k]) for k in 'xy'}
    #     z = self._maybe_repeat_values(self._data.data)

    #     dim_1d, dim_2d = self._get_dims_of_1d_and_2d_coords()
    #     if dim_2d is None:
    #         return xy['x'].values, xy['y'].values, z

    #     # Broadcast 1d coord to 2d and repeat along 1d dim
    #     # TODO: It may be more efficient here to first repeat and then broadcast, but
    #     # the current order is simpler in implementation.
    #     broadcasted_coord = repeat(sc.broadcast(xy[dim_1d[0]],
    #                                             sizes={
    #                                                 **xy[dim_2d[0]].sizes,
    #                                                 **xy[dim_1d[0]].sizes
    #                                             }).transpose(self._data.dims),
    #                                dim=dim_1d[1],
    #                                n=2)

    #     # Repeat 2d coord along 1d dim
    #     repeated_coord = repeat(xy[dim_2d[0]].transpose(self._data.dims),
    #                             dim=dim_1d[1],
    #                             n=2)

    #     out = {
    #         dim_1d[0]: broadcasted_coord[dim_1d[1], 1:-1].values,
    #         dim_2d[0]: repeated_coord.values
    #     }

    #     return out['x'], out['y'], z

    def _make_mesh(self, shading='auto', rasterized=True, **kwargs):
        x, y, z = _from_data_array_to_pcolormesh(data=self._data.data,
                                                 coords=self._bin_edge_coords)
        self._mesh = self._ax.pcolormesh(x.values,
                                         y.values,
                                         z.values,
                                         cmap=self.color_mapper.cmap,
                                         shading=shading,
                                         rasterized=rasterized,
                                         **kwargs)
        if self._cbar:
            self._cbar = colorbar(self._mesh,
                                  ax=self._ax,
                                  cax=self._cax,
                                  extend=self._extend,
                                  label=name_with_unit(var=self._data.data, name=""))

            # Add event that toggles the norm of the colorbar when clicked on
            # TODO: change this to a double-click event once this is supported in
            # jupyterlab, see https://github.com/matplotlib/ipympl/pull/446
            self._cbar.ax.set_picker(5)
            self._ax.figure.canvas.mpl_connect('pick_event', self.toggle_norm)
            self._cbar.ax.yaxis.set_label_coords(-1.1, 0.5)
        self._mesh.set_array(None)
        self._set_norm()
        # self._update_colors()
        self._set_mesh_colors()

    # def _rescale_colormap(self):
    #     """
    #     """
    #     vmin, vmax = fix_empty_range(find_limits(self._data.data,
    #                                              scale=self._norm_flag))
    #     if self._user_vmin is not None:
    #         assert self._user_vmin.unit == self._data.unit
    #         self._vmin = self._user_vmin.value
    #     elif vmin.value < self._vmin:
    #         self._vmin = vmin.value
    #     if self._user_vmax is not None:
    #         assert self._user_vmax.unit == self._data.unit
    #         self._vmax = self._user_vmax.value
    #     elif vmax.value > self._vmax:
    #         self._vmax = vmax.value

    #     self._norm_func.vmin = self._vmin
    #     self._norm_func.vmax = self._vmax

    def _set_clim(self):
        self._mesh.set_clim(self.color_mapper.vmin, self.color_mapper.vmax)

    # def _update_colors(self):
    #     flat_values = self._maybe_repeat_values(self._data.data).flatten()
    #     self._rgba = self._cmap(self._norm_func(flat_values))
    #     if len(self._data.masks) > 0:
    #         one_mask = self._maybe_repeat_values(
    #             sc.broadcast(reduce(lambda a, b: a | b, self._data.masks.values()),
    #                          dims=self._data.dims,
    #                          shape=self._data.shape)).flatten()
    #         self._rgba[one_mask] = self._mask_cmap(
    #             self._norm_func(flat_values[one_mask]))
    # self._mesh.set_facecolors(rgba)

    def _set_mesh_colors(self):
        # flat_values = self._maybe_repeat_values(self._data.data).flatten()
        # rgba = self._cmap(self._norm_func(flat_values))
        # if len(self._data.masks) > 0:
        #     one_mask = self._maybe_repeat_values(
        #         sc.broadcast(reduce(lambda a, b: a | b, self._data.masks.values()),
        #                      dims=self._data.dims,
        #                      shape=self._data.shape)).flatten()
        #     rgba[one_mask] = self._mask_cmap(self._norm_func(flat_values[one_mask]))

        to_mapper = sc.DataArray(data=_maybe_repeat_values(
            data=self._data.data, coords=self._bin_edge_coords))
        if self._data.masks:
            to_mapper.masks['one_mask'] = _maybe_repeat_values(
                data=sc.broadcast(reduce(lambda a, b: a | b, self._data.masks.values()),
                                  dims=self._data.dims,
                                  shape=self._data.shape),
                coords=self._bin_edge_coords)

        rgba = self.color_mapper.rgba(data=to_mapper)
        self._mesh.set_facecolors(rgba.reshape(np.prod(rgba.shape[:-1]), 4))

    def update(self, new_values: sc.DataArray):
        """
        Update image array with new values.
        """
        # # self._rescale_colormap()
        # # self._set_clim()
        # # self._set_mesh_colors()
        # to_update = sc.DataArray(data=self._maybe_repeat_values(new_values.data))
        # if new_values.masks:
        #     to_update.masks['one_mask'] = self._maybe_repeat_values(
        #         sc.broadcast(reduce(lambda a, b: a | b, new_values.masks.values()),
        #                      dims=new_values.dims,
        #                      shape=new_values.shape)).flatten()
        #     # rgba[one_mask] = self._mask_cmap(self._norm_func(flat_values[one_mask]))
        # # super().update(new_values=to_update)
        self._data = new_values
        self.color_mapper.rescale(data=new_values.data)
        self._set_clim()
        self._set_mesh_colors()

    def _set_norm(self):
        # func = dict(linear=Normalize, log=LogNorm)[self._norm_flag]
        # self._norm_func = func()
        # self._rescale_colormap()
        self.color_mapper.set_norm(data=self._data.data)
        self._mesh.set_norm(self.color_mapper.norm_func)
        self._set_clim()

    def toggle_norm(self, event):
        if event.artist is not self._cbar.ax:
            return
        # self._norm_flag = "log" if self._norm_flag == "linear" else "linear"
        # self._vmin = np.inf
        # self._vmax = np.NINF
        self.color_mapper.toggle_norm()
        self._set_norm()
        self._set_mesh_colors()
        self._ax.figure.canvas.draw_idle()

    def get_limits(self, xscale, yscale):
        # xmin, xmax = fix_empty_range(
        #     find_limits(coord_as_bin_edges(self._data, self._dims['x']), scale=xscale))
        # ymin, ymax = fix_empty_range(
        #     find_limits(coord_as_bin_edges(self._data, self._dims['y']), scale=yscale))
        xmin, xmax = fix_empty_range(
            find_limits(self._bin_edge_coords['x']['var'], scale=xscale))
        ymin, ymax = fix_empty_range(
            find_limits(self._bin_edge_coords['y']['var'], scale=yscale))
        return (sc.concat([xmin, xmax], dim=self._dims['x']),
                sc.concat([ymin, ymax], dim=self._dims['y']))
