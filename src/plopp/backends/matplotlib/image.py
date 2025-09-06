# # SPDX-License-Identifier: BSD-3-Clause
# # Copyright (c) 2025 Scipp contributors (https://github.com/scipp)

# import scipp as sc

# from .canvas import Canvas
# from .fast_image import FastImage
# from .mesh_image import MeshImage


# def Image(
#     canvas: Canvas,
#     data: sc.DataArray,
#     **kwargs,
# ):
#     """
#     Factory function to create an image artist.
#     If all the coordinates of the data are 1D and linearly spaced,
#     a `FastImage` is created.
#     Otherwise, a `MeshImage` is created.

#     Parameters
#     ----------
#     canvas:
#         The canvas that will display the image.
#     data:
#         The data to create the image from.
#     """
#     if (canvas.ax.name != 'polar') and all(
#         (data.coords[dim].ndim < 2)
#         and ((data.coords[dim].dtype == str) or (sc.islinspace(data.coords[dim])))
#         for dim in data.dims
#     ):
#         return FastImage(canvas=canvas, data=data, **kwargs)
#     else:
#         return MeshImage(canvas=canvas, data=data, **kwargs)


# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Scipp contributors (https://github.com/scipp)

import uuid
import warnings
from typing import Literal

import numpy as np
import scipp as sc
from matplotlib.collections import QuadMesh
from matplotlib.image import AxesImage

from ...core.utils import coord_as_bin_edges, merge_masks, repeat, scalar_to_string
from ...graphics.bbox import BoundingBox, axis_bounds
from ...graphics.colormapper import ColorMapper
from ..common import check_ndim
from .canvas import Canvas


def _suitable_for_fast_image(canvas: Canvas, data: sc.DataArray) -> bool:
    return (canvas.ax.name != 'polar') and all(
        (data.coords[dim].ndim < 2)
        and ((data.coords[dim].dtype == str) or (sc.islinspace(data.coords[dim])))
        for dim in data.dims
    )


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


class Image:
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
        self._shading = shading
        self._rasterized = rasterized
        self._kwargs = kwargs
        self._optimized_mode = _suitable_for_fast_image(self._canvas, self._data)

        # # If the grid is visible on the axes, we need to set that on again after we
        # # call pcolormesh, because that turns the grid off automatically.
        # # See https://github.com/matplotlib/matplotlib/issues/15600.
        # need_grid = self._ax.xaxis.get_gridlines()[0].get_visible()
        # # # Calling imshow sets the aspect ratio to 'equal', which might not be what the
        # # # user requested. We need to restore the original aspect ratio after making the
        # # # image.
        # # original_aspect = self._ax.get_aspect()

        self._string_labels = {}
        self._bin_edge_coords = {}
        self._raw_coords = {}
        to_dim_search = {
            k: {'dim': self._data.dims[i], 'var': self._data.coords[self._data.dims[i]]}
            for i, k in enumerate('yx')
        }

        self._update_coords()
        self._dim_1d, self._dim_2d = _get_dims_of_1d_and_2d_coords(to_dim_search)

        self._image = self._make_image()

        self._colormapper.add_artist(self.uid, self)
        self._update_colors()

        for xy, var in self._string_labels.items():
            getattr(self._ax, f'set_{xy}ticks')(np.arange(float(var.shape[0])))
            getattr(self._ax, f'set_{xy}ticklabels')(var.values)

        # if need_grid:
        #     self._ax.grid(True)

        self._canvas.register_format_coord(self.format_coord)

    def _update_coords(self) -> None:
        self._data_with_bin_edges = sc.DataArray(data=self._data.data)
        for i, k in enumerate('yx'):
            self._raw_coords[k] = self._data.coords[self._data.dims[i]]
            self._bin_edge_coords[k] = coord_as_bin_edges(
                self._data, self._data.dims[i]
            )
            self._data_with_bin_edges.coords[self._data.dims[i]] = (
                self._bin_edge_coords[k]
            )
            if self._data.coords[self._data.dims[i]].dtype == str:
                self.string_labels[k] = self._data.coords[self._data.dims[i]]

        if self._optimized_mode:
            self._xmin, self._xmax = self._bin_edge_coords["x"].values[[0, -1]]
            self._ymin, self._ymax = self._bin_edge_coords["y"].values[[0, -1]]
            self._dx = np.diff(self._bin_edge_coords["x"].values[:2])
            self._dy = np.diff(self._bin_edge_coords["y"].values[:2])

    def _make_image(self) -> QuadMesh | AxesImage:
        if self._optimized_mode:
            # Calling imshow sets the aspect ratio to 'equal', which might not be what the
            # user requested. We need to restore the original aspect ratio after making the
            # image.
            original_aspect = self._ax.get_aspect()

            # Because imshow sets the aspect, it may generate warnings when the axes scales
            # are log.
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    category=UserWarning,
                    message="Attempt to set non-positive .* on a log-scaled axis",
                )
                img = self._ax.imshow(
                    self._data.values,
                    origin="lower",
                    extent=(self._xmin, self._xmax, self._ymin, self._ymax),
                    **({"interpolation": "nearest"} | self._kwargs),
                )

            self._ax.set_aspect(original_aspect)
            return img

        else:
            # self._optimized_mode = False
            # If the grid is visible on the axes, we need to set that on again after we
            # call pcolormesh, because that turns the grid off automatically.
            # See https://github.com/matplotlib/matplotlib/issues/15600.
            need_grid = self._ax.xaxis.get_gridlines()[0].get_visible()

            x, y, z = _from_data_array_to_pcolormesh(
                data=self._data.data,
                coords=self._bin_edge_coords,
                dim_1d=self._dim_1d,
                dim_2d=self._dim_2d,
            )
            mesh = self._ax.pcolormesh(
                x.values,
                y.values,
                z.values,
                shading=self._shading,
                rasterized=self._rasterized,
                **self._kwargs,
            )
            mesh.set_array(None)
            if need_grid:
                self._ax.grid(True)
            return mesh

    @property
    def data(self):
        """
        Get the Image's data in a form that may have been tweaked, compared to the
        original data, in the case of a two-dimensional coordinate.
        """
        if self._optimized_mode:
            return self._data
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
        if self._optimized_mode:
            self._image.set_data(rgba)
        else:
            self._image.set_facecolors(rgba.reshape(np.prod(rgba.shape[:-1]), 4))

    def update(self, new_values: sc.DataArray):
        """
        Update image array with new values.

        Parameters
        ----------
        new_values:
            New data to update the mesh values from.
        """
        check_ndim(new_values, ndim=2, origin='MeshImage')
        old_shape = self._data.shape
        old_mode = self._optimized_mode
        self._data = new_values
        self._optimized_mode = _suitable_for_fast_image(self._canvas, self._data)
        print("self._optimized_mode:", self._optimized_mode)
        if old_mode != self._optimized_mode:
            self._image.remove()
            self._image = self._make_image()
        elif self._data.shape != old_shape:
            self._update_coords()
            if self._optimized_mode:
                self._image.set_extent((self._xmin, self._xmax, self._ymin, self._ymax))
            else:
                self._image.remove()
                self._image = self._make_image()
        elif any(
            not sc.identical(new_values.coords[self._data.dims[i]], self._raw_coords[k])
            for i, k in enumerate('yx')
        ):
            # Update the coordinates of the existing mesh
            self._update_coords()
            if self._optimized_mode:
                self._image.set_extent((self._xmin, self._xmax, self._ymin, self._ymax))
            else:
                x, y, _ = _from_data_array_to_pcolormesh(
                    data=self._data.data,
                    coords=self._bin_edge_coords,
                    dim_1d=self._dim_1d,
                    dim_2d=self._dim_2d,
                )
                m = QuadMesh(np.stack(np.meshgrid(x.values, y.values), axis=-1))
                # TODO: There is no public API to update the coordinates of a QuadMesh,
                # so we have to access the protected member here.
                self._image._coordinates = m._coordinates
                self._image.stale = True  # mark it for re-draw
        else:
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
        return self._image.get_visible()

    @visible.setter
    def visible(self, val: bool):
        self._image.set_visible(val)

    @property
    def opacity(self) -> float:
        """
        The opacity of the image.
        """
        return self._image.get_alpha()

    @opacity.setter
    def opacity(self, val: float):
        self._image.set_alpha(val)

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
        self._image.remove()
        self._colormapper.remove_artist(self.uid)
