# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Scipp contributors (https://github.com/scipp)

import uuid
from typing import Literal

import numpy as np
import scipp as sc

from ...core.utils import coord_as_bin_edges, merge_masks, repeat, scalar_to_string
from ...graphics.bbox import BoundingBox, axis_bounds
from ...graphics.colormapper import ColorMapper
from ..common import check_ndim
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
    broadcasted_coord = repeat(
        sc.broadcast(
            coords[dim_1d[0]],
            sizes={**coords[dim_2d[0]].sizes, **coords[dim_1d[0]].sizes},
        ).transpose(data.dims),
        dim=dim_1d[1],
        n=2,
    )
    # Repeat 2d coord along 1d dim
    repeated_coord = repeat(coords[dim_2d[0]].transpose(data.dims), dim=dim_1d[1], n=2)
    out = {dim_1d[0]: broadcasted_coord[dim_1d[1], 1:-1], dim_2d[0]: repeated_coord}
    return out['x'], out['y'], z


class MeshImage:
    """
    Artist to represent two-dimensional data.

    Parameters
    ----------
    canvas:
        The canvas that will display the image.
    colormapper:
        The colormapper to use for the image.
    data:
        The initial data to create the image from.
    artist_number:
        The canvas keeps track of how many images have been added to it. This is unused
        by the MeshImage artist.
    uid:
        The unique identifier of the artist. If None, a random UUID is generated.
    shading:
        The shading to use for the ``pcolormesh``.
    rasterized:
        Rasterize the mesh/image if ``True``.
    **kwargs:
        Additional arguments are forwarded to Matplotlib's ``pcolormesh``.
    """

    def __init__(
        self,
        canvas: Canvas,
        colormapper: ColorMapper,
        data: sc.DataArray,
        artist_number: int,
        uid: str | None = None,
        shading: str = 'auto',
        rasterized: bool = True,
        **kwargs,
    ):
        check_ndim(data, ndim=2, origin='MeshImage')
        self.uid = uid if uid is not None else uuid.uuid4().hex
        self._canvas = canvas
        self._colormapper = colormapper
        self._ax = self._canvas.ax
        self._data = data
        # If the grid is visible on the axes, we need to set that on again after we
        # call pcolormesh, because that turns the grid off automatically.
        # See https://github.com/matplotlib/matplotlib/issues/15600.
        need_grid = self._ax.xaxis.get_gridlines()[0].get_visible()

        to_dim_search = {}
        string_labels = {}
        bin_edge_coords = {}
        self._data_with_bin_edges = sc.DataArray(data=self._data.data)
        for i, k in enumerate('yx'):
            to_dim_search[k] = {
                'dim': self._data.dims[i],
                'var': self._data.coords[self._data.dims[i]],
            }
            bin_edge_coords[k] = coord_as_bin_edges(self._data, self._data.dims[i])
            self._data_with_bin_edges.coords[self._data.dims[i]] = bin_edge_coords[k]
            if self._data.coords[self._data.dims[i]].dtype == str:
                string_labels[k] = self._data.coords[self._data.dims[i]]

        self._dim_1d, self._dim_2d = _get_dims_of_1d_and_2d_coords(to_dim_search)
        self._mesh = None

        x, y, z = _from_data_array_to_pcolormesh(
            data=self._data.data,
            coords=bin_edge_coords,
            dim_1d=self._dim_1d,
            dim_2d=self._dim_2d,
        )
        self._mesh = self._ax.pcolormesh(
            x.values,
            y.values,
            z.values,
            shading=shading,
            rasterized=rasterized,
            **kwargs,
        )

        self._colormapper.add_artist(self.uid, self)
        self._mesh.set_array(None)
        self._update_colors()

        for xy, var in string_labels.items():
            getattr(self._ax, f'set_{xy}ticks')(np.arange(float(var.shape[0])))
            getattr(self._ax, f'set_{xy}ticklabels')(var.values)

        if need_grid:
            self._ax.grid(True)

        self._canvas.register_format_coord(self.format_coord)

    @property
    def data(self):
        """
        Get the Mesh's data in a form that may have been tweaked, compared to the
        original data, in the case of a two-dimensional coordinate.
        """
        out = sc.DataArray(
            data=_maybe_repeat_values(
                data=self._data.data, dim_1d=self._dim_1d, dim_2d=self._dim_2d
            )
        )
        if self._data.masks:
            out.masks['one_mask'] = _maybe_repeat_values(
                data=sc.broadcast(
                    merge_masks(self._data.masks), sizes=self._data.sizes
                ),
                dim_1d=self._dim_1d,
                dim_2d=self._dim_2d,
            )
        return out

    def notify_artist(self, message: str) -> None:
        """
        Receive notification from the colormapper that its state has changed.
        We thus need to update the colors of the mesh.

        Parameters
        ----------
        message:
            The message from the colormapper.
        """
        self._update_colors()

    def _update_colors(self):
        """
        Update the mesh colors.
        """
        rgba = self._colormapper.rgba(self.data)
        self._mesh.set_facecolors(rgba.reshape(np.prod(rgba.shape[:-1]), 4))

    def update(self, new_values: sc.DataArray):
        """
        Update image array with new values.

        Parameters
        ----------
        new_values:
            New data to update the mesh values from.
        """
        check_ndim(new_values, ndim=2, origin='MeshImage')
        self._data = new_values
        self._data_with_bin_edges.data = new_values.data
        self._update_colors()

    def format_coord(
        self, xslice: tuple[str, sc.Variable], yslice: tuple[str, sc.Variable]
    ) -> str:
        """
        Format the coordinates of the mouse pointer to show the value of the
        data at that point.

        Parameters
        ----------
        xslice:
            Dimension and x coordinate of the mouse pointer, as slice parameters.
        yslice:
            Dimension and y coordinate of the mouse pointer, as slice parameters.
        """
        try:
            val = self._data_with_bin_edges[yslice][xslice]
            prefix = self._data.name
            if prefix:
                prefix += ': '
            return prefix + scalar_to_string(val)
        except (IndexError, RuntimeError):
            return None

    @property
    def visible(self) -> bool:
        """
        The visibility of the image.
        """
        return self._mesh.get_visible()

    @visible.setter
    def visible(self, val: bool):
        self._mesh.set_visible(val)

    @property
    def opacity(self) -> float:
        """
        The opacity of the image.
        """
        return self._mesh.get_alpha()

    @opacity.setter
    def opacity(self, val: float):
        self._mesh.set_alpha(val)

    def bbox(self, xscale: Literal['linear', 'log'], yscale: Literal['linear', 'log']):
        """
        The bounding box of the image.
        """
        ydim, xdim = self._data.dims
        image_x = self._data_with_bin_edges.coords[xdim]
        image_y = self._data_with_bin_edges.coords[ydim]

        return BoundingBox(
            **{**axis_bounds(('xmin', 'xmax'), image_x, xscale)},
            **{**axis_bounds(('ymin', 'ymax'), image_y, yscale)},
        )

    def remove(self):
        """
        Remove the image artist from the canvas.
        """
        self._mesh.remove()
        self._colormapper.remove_artist(self.uid)
