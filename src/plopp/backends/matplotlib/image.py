# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import uuid

import numpy as np
import scipp as sc

from ...core.utils import coord_as_bin_edges, merge_masks, repeat
from .canvas import Canvas


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


class Image:
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

        self._canvas = canvas
        self._ax = self._canvas.ax
        self._data = data
        self._id = uuid.uuid4().hex
        # Because all keyword arguments from the figure are forwarded to both the canvas
        # and the line, we need to remove the arguments that belong to the canvas.
        kwargs.pop('ax', None)
        kwargs.pop('cax', None)
        # If the grid is visible on the axes, we need to set that on again after we
        # call pcolormesh, because that turns the grid off automatically.
        # See https://github.com/matplotlib/matplotlib/issues/15600.
        need_grid = self._ax.xaxis.get_gridlines()[0].get_visible()

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
        self._mesh = None

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

        if need_grid:
            self._ax.grid(True)

    @property
    def data(self):
        """
        Get the Mesh's data in a form that may have been tweaked, compared to the
        original data, in the case of a two-dimensional coordinate.
        """
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

    def set_colors(self, rgba: np.ndarray):
        """
        Set the mesh's rgba colors:

        Parameters
        ----------
        rgba:
            The array of rgba colors.
        """
        self._mesh.set_facecolors(rgba.reshape(np.prod(rgba.shape[:-1]), 4))
        self._canvas.draw()

    def update(self, new_values: sc.DataArray):
        """
        Update image array with new values.

        Parameters
        ----------
        new_values:
            New data to update the mesh values from.
        """
        self._data = new_values
