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


def _maybe_repeat_values(data, coords):
    dim_1d, dim_2d = _get_dims_of_1d_and_2d_coords(coords)
    if dim_2d is None:
        return data
    return repeat(data, dim=dim_1d[1], n=2)[dim_1d[1], :-1]


def _from_data_array_to_pcolormesh(data, coords):
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
                                                 coords=self._bin_edge_coords)
        self._mesh = self._ax.pcolormesh(x.values,
                                         y.values,
                                         z.values,
                                         shading=shading,
                                         rasterized=rasterized,
                                         **kwargs)
        self._mesh.set_array(None)

    @property
    def data(self):
        out = sc.DataArray(data=_maybe_repeat_values(data=self._data.data,
                                                     coords=self._bin_edge_coords))
        if self._data.masks:
            out.masks['one_mask'] = _maybe_repeat_values(data=sc.broadcast(
                merge_masks(self._data.masks),
                dims=self._data.dims,
                shape=self._data.shape),
                                                         coords=self._bin_edge_coords)
        return out

    def set_colors(self, rgba):
        self._mesh.set_facecolors(rgba.reshape(np.prod(rgba.shape[:-1]), 4))

    def update(self, new_values: sc.DataArray):
        """
        Update image array with new values.
        """
        self._data = new_values
