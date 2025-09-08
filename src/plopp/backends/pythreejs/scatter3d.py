# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)
import uuid
from typing import Literal

import numpy as np
import scipp as sc
from matplotlib.colors import to_rgb

from ...core.limits import find_limits
from ...graphics.bbox import BoundingBox
from ...graphics.colormapper import ColorMapper
from ..common import check_ndim
from .canvas import Canvas


class Scatter3d:
    """
    Artist to represent a three-dimensional point cloud/scatter plot.

    Parameters
    ----------
    canvas:
        The canvas that will display the scatter plot.
    x:
        The name of the coordinate that is to be used for the X positions.
    y:
        The name of the coordinate that is to be used for the Y positions.
    z:
        The name of the coordinate that is to be used for the Z positions.
    data:
        The initial data to create the line from.
    uid:
        The unique identifier of the artist. If None, a random UUID is generated.
    size:
        The size of the markers.
    color:
        The color of the markers (this is ignored if a colorbar is used).
    colormapper:
        The colormapper to use for the scatter plot.
    artist_number:
        Number of the artist (can be used to set the color of the artist).
    opacity:
        The opacity of the points.
    pixel_size:
        The size of the pixels in the plot. Deprecated (use size instead).
    """

    def __init__(
        self,
        *,
        canvas: Canvas,
        x: str,
        y: str,
        z: str,
        data: sc.DataArray,
        uid: str | None = None,
        size: sc.Variable | float = 1,
        color: str | None = None,
        colormapper: ColorMapper | None = None,
        artist_number: int = 0,
        opacity: float = 1,
        pixel_size: sc.Variable | float | None = None,
    ):
        check_ndim(data, ndim=1, origin='Scatter3d')
        self.uid = uid if uid is not None else uuid.uuid4().hex
        self._canvas = canvas
        self._colormapper = colormapper
        self._data = data
        self._x = x
        self._y = y
        self._z = z
        self._opacity = opacity
        self._trash = None

        # TODO: remove pixel_size in the next release
        self._size = size if pixel_size is None else pixel_size
        if hasattr(self._size, 'unit'):
            if len({self._data.coords[dim].unit for dim in [x, y, z]}) > 1:
                raise ValueError(
                    f'The supplied size has unit {self._size.unit}, but '
                    'the spatial coordinates do not all have the same units. In this '
                    'case the size should just be a float with no unit.'
                )
            else:
                self._size = self._size.to(
                    dtype=float, unit=self._data.coords[x].unit
                ).value

        self._make_point_cloud()

        if self._colormapper is not None:
            self._colormapper.add_artist(self.uid, self)
        else:
            colors = np.broadcast_to(
                np.array(to_rgb(f'C{artist_number}' if color is None else color)),
                (self._data.coords[self._x].shape[0], 3),
            ).astype('float32')
            self.geometry.attributes["color"].array = colors
            self._new_colors = None

        self._canvas.add(self.points)

    def _make_point_cloud(self) -> None:
        """
        Create the point cloud geometry and material.
        """
        import pythreejs as p3

        self._backup_coords()

        self.geometry = p3.BufferGeometry(
            attributes={
                'position': p3.BufferAttribute(
                    array=np.array(
                        [
                            self._data.coords[self._x].values.astype('float32'),
                            self._data.coords[self._y].values.astype('float32'),
                            self._data.coords[self._z].values.astype('float32'),
                        ]
                    ).T
                ),
                'color': p3.BufferAttribute(
                    array=np.zeros(
                        (self._data.coords[self._x].shape[0], 3), dtype='float32'
                    )
                ),
            }
        )
        self._new_positions = None

        # TODO: a device pixel_ratio should probably be read from a config file
        pixel_ratio = 1.0
        # Note that an additional factor of 2.5 (obtained from trial and error) seems to
        # be required to get the sizes right in the scene.
        self.material = p3.PointsMaterial(
            vertexColors='VertexColors',
            size=2.5 * self._size * pixel_ratio,
            transparent=True,
            opacity=self._opacity,
        )
        self.points = p3.Points(geometry=self.geometry, material=self.material)

    def _backup_coords(self) -> None:
        """
        Backup the current coordinates to be able to detect changes.
        """
        self._old_coords = {
            self._x: self._data.coords[self._x],
            self._y: self._data.coords[self._y],
            self._z: self._data.coords[self._z],
        }

    def notify_artist(self, message: str) -> None:
        """
        Receive notification from the colormapper that its state has changed.
        We thus need to update the colors of the points.

        Parameters
        ----------
        message:
            The message from the colormapper.
        """
        self._new_colors = self._colormapper.rgba(self.data)[..., :3].astype('float32')

        # Second call to finalize: this will be the final call if there is a
        # colormapper. The first call was made by update() once the positions were
        # updated.
        self._finalize_update(2)

    def _update_positions(self) -> None:
        """
        Update the point cloud's positions from the data.
        """
        if all(
            sc.identical(self._old_coords[dim], self._data.coords[dim])
            for dim in [self._x, self._y, self._z]
        ):
            return
        self._backup_coords()
        return np.stack(
            [
                self._data.coords[self._x].values.astype('float32'),
                self._data.coords[self._y].values.astype('float32'),
                self._data.coords[self._z].values.astype('float32'),
            ],
            axis=1,
        )

    def update(self, new_values):
        """
        Update point cloud array with new values.

        Parameters
        ----------
        new_values:
            New data to update the point cloud values from.
        """
        check_ndim(new_values, ndim=1, origin='Scatter3d')
        old_shape = self._data.shape
        self._data = new_values

        if self._data.shape != old_shape:
            self._trash = self.points
            self._make_point_cloud()
        else:
            self._trash = None
            self._new_positions = self._update_positions()

        # First call to finalize: this will be the final call if there is no
        # colormapper. If there is a colormapper, it will call finalize again once it
        # has updated the colors.
        self._finalize_update(1)

    def _finalize_update(self, count: int) -> None:
        """
        Finalize the update of the point cloud.
        This is called twice if there is a colormapper:
        once when the positions are updated, and once when the colors are updated.
        We want to wait for both to be ready before updating the geometry.
        """
        if count < (1 + bool(self._colormapper is not None)):
            return
        with self._canvas.renderer.hold():
            if self._new_positions is not None:
                self.geometry.attributes["position"].array = self._new_positions
                self._new_positions = None
            if self._new_colors is not None:
                self.geometry.attributes["color"].array = self._new_colors
                self._new_colors = None
            if self._trash is not None:
                self._canvas.remove(self._trash)
                self._trash = None
                self._canvas.add(self.points)

    @property
    def opacity(self) -> float:
        """
        The scatter points opacity.
        """
        return self.material.opacity

    @opacity.setter
    def opacity(self, val: float):
        self.material.opacity = val
        self.material.depthTest = val > 0.5

    @property
    def visible(self) -> bool:
        """
        The visibility of the scatter points.
        """
        return self.points.visible

    @visible.setter
    def visible(self, val: bool):
        self.points.visible = val

    @property
    def data(self):
        """
        Get the point cloud data.
        """
        return self._data

    def bbox(
        self,
        xscale: Literal['linear', 'log'],
        yscale: Literal['linear', 'log'],
        zscale: Literal['linear', 'log'],
    ) -> BoundingBox:
        """
        The bounding box of the scatter points.
        """
        padding = 0.5 * self._size
        xbounds = find_limits(self._data.coords[self._x], scale=xscale)
        ybounds = find_limits(self._data.coords[self._y], scale=yscale)
        zbounds = find_limits(self._data.coords[self._z], scale=zscale)
        return BoundingBox(
            xmin=xbounds[0].value - padding,
            xmax=xbounds[1].value + padding,
            ymin=ybounds[0].value - padding,
            ymax=ybounds[1].value + padding,
            zmin=zbounds[0].value - padding,
            zmax=zbounds[1].value + padding,
        )

    def remove(self) -> None:
        """
        Remove the point cloud from the canvas.
        """
        self._canvas.remove(self.points)
        if self._colormapper is not None:
            self._colormapper.remove_artist(self.uid)
