# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core.utils import coord_as_bin_edges, repeat, merge_masks

import numpy as np
import scipp as sc
from typing import Any


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


def _maybe_repeat_values(data, dim_1d, dim_2d):
    if dim_2d is None:
        return data
    return repeat(data, dim=dim_1d[1], n=2)[dim_1d[1], :-1]


def _from_data_array_to_pcolormesh(data, coords, dim_1d, dim_2d):
    z = _maybe_repeat_values(data=data, dim_1d=dim_1d, dim_2d=dim_2d)
    if dim_2d is None:
        return coords['x'], coords['y'], z

    # Broadcast 1d coord to 2d and repeat along 1d dim
    # TODO: It may be more efficient here to first repeat and then broadcast, but
    # the current order is simpler in implementation.
    broadcasted_coord = repeat(sc.broadcast(coords[dim_1d[0]],
                                            sizes={
                                                **coords[dim_2d[0]].sizes,
                                                **coords[dim_1d[0]].sizes
                                            }).transpose(data.dims),
                               dim=dim_1d[1],
                               n=2)
    # Repeat 2d coord along 1d dim
    repeated_coord = repeat(coords[dim_2d[0]].transpose(data.dims), dim=dim_1d[1], n=2)
    out = {dim_1d[0]: broadcasted_coord[dim_1d[1], 1:-1], dim_2d[0]: repeated_coord}
    return out['x'], out['y'], z


class Mesh:
    """
    Class for 2 dimensional plots.
    """

    def __init__(self,
                 canvas,
                 data,
                 cax: Any = None,
                 cmap: str = 'viridis',
                 mask_cmap: str = 'gray',
                 norm: str = 'linear',
                 vmin=None,
                 vmax=None,
                 cbar=True,
                 shading='auto',
                 rasterized=True,
                 **kwargs):

        self._ax = canvas.ax
        self._data = data

        to_dim_search = {}
        string_labels = {}
        bin_edge_coords = {}
        for i, k in enumerate('yx'):
            to_dim_search[k] = {
                'dim': self._data.dims[i],
                'var': self._data.meta[self._data.dims[i]]
            }
            bin_edge_coords[k] = coord_as_bin_edges(self._data, self._data.dims[i])
            if self._data.meta[self._data.dims[i]].dtype == str:
                string_labels[k] = self._data.meta[self._data.dims[i]]

        self._dim_1d, self._dim_2d = _get_dims_of_1d_and_2d_coords(to_dim_search)
        self._xlabel = None
        self._ylabel = None
        self._title = None
        self._cax = cax
        self._mesh = None
        self._cbar = cbar

        self._extend = 'neither'
        if (vmin is not None) and (vmax is not None):
            self._extend = 'both'
        elif vmin is not None:
            self._extend = 'min'
        elif vmax is not None:
            self._extend = 'max'

        x, y, z = _from_data_array_to_pcolormesh(data=self._data.data,
                                                 coords=bin_edge_coords,
                                                 dim_1d=self._dim_1d,
                                                 dim_2d=self._dim_2d)
        self._mesh = self._ax.pcolormesh(x.values,
                                         y.values,
                                         z.values,
                                         shading=shading,
                                         rasterized=rasterized,
                                         **kwargs)
        self._mesh.set_array(None)

        for xy, var in string_labels.items():
            getattr(self._ax, f'set_{xy}ticks')(np.arange(float(var.shape[0])))
            getattr(self._ax, f'set_{xy}ticklabels')(var.values)

    @property
    def data(self):
        out = sc.DataArray(data=_maybe_repeat_values(
            data=self._data.data, dim_1d=self._dim_1d, dim_2d=self._dim_2d))
        if self._data.masks:
            out.masks['one_mask'] = _maybe_repeat_values(data=sc.broadcast(
                merge_masks(self._data.masks),
                dims=self._data.dims,
                shape=self._data.shape),
                                                         dim_1d=self._dim_1d,
                                                         dim_2d=self._dim_2d)
        return out

    def set_colors(self, rgba):
        self._mesh.set_facecolors(rgba.reshape(np.prod(rgba.shape[:-1]), 4))

    def update(self, new_values: sc.DataArray):
        """
        Update image array with new values.
        """
        self._data = new_values
