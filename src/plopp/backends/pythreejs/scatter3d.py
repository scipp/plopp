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
        import pythreejs as p3

        check_ndim(data, ndim=1, origin='Scatter3d')
        self.uid = uid if uid is not None else uuid.uuid4().hex
        self._canvas = canvas
        self._colormapper = colormapper
        self._data = data
        self._x = x
        self._y = y
        self._z = z

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

        if self._colormapper is not None:
            self._colormapper.add_artist(self.uid, self)
            colors = self._colormapper.rgba(self.data)[..., :3].astype('float32')
        else:
            colors = np.broadcast_to(
                np.array(to_rgb(f'C{artist_number}' if color is None else color)),
                (self._data.coords[self._x].shape[0], 3),
            ).astype('float32')

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
                'color': p3.BufferAttribute(array=colors),
            }
        )

        # TODO: a device pixel_ratio should probably be read from a config file
        pixel_ratio = 1.0
        # Note that an additional factor of 2.5 (obtained from trial and error) seems to
        # be required to get the sizes right in the scene.
        self.material = p3.PointsMaterial(
            vertexColors='VertexColors',
            size=2.5 * self._size * pixel_ratio,
            transparent=True,
            opacity=opacity,
        )
        self.points = p3.Points(geometry=self.geometry, material=self.material)
        self._canvas.add(self.points)

    def notify_artist(self, message: str) -> None:
        """
        Receive notification from the colormapper that its state has changed.
        We thus need to update the colors of the points.

        Parameters
        ----------
        message:
            The message from the colormapper.
        """
        self._update_colors()

    def _update_colors(self):
        """
        Set the point cloud's rgba colors:
        """
        self.geometry.attributes["color"].array = self._colormapper.rgba(self.data)[
            ..., :3
        ].astype('float32')

    def update(self, new_values):
        """
        Update point cloud array with new values.

        Parameters
        ----------
        new_values:
            New data to update the point cloud values from.
        """
        check_ndim(new_values, ndim=1, origin='Scatter3d')
        self._data = new_values
        if self._colormapper is not None:
            self._update_colors()

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
