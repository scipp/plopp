# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import uuid
from typing import Literal

import numpy as np
import scipp as sc

from ...graphics.bbox import BoundingBox, axis_bounds
from .canvas import Canvas


def _check_ndim(data):
    if data.ndim != 1:
        raise ValueError(
            'PointCloud only accepts one dimensional data, '
            f'found {data.ndim} dimensions. You should flatten your data '
            '(using scipp.flatten) before sending it to the point cloud.'
        )


class Scatter3d:
    """
    Artist to represent a three-dimensional point cloud/scatter plot.

    Parameters
    ----------
    x:
        The name of the coordinate that is to be used for the X positions.
    y:
        The name of the coordinate that is to be used for the Y positions.
    z:
        The name of the coordinate that is to be used for the Z positions.
    data:
        The initial data to create the line from.
    size:
        The size of the markers.
    opacity:
        The opacity of the points.
    """

    def __init__(
        self,
        *,
        canvas: Canvas,
        x: str,
        y: str,
        z: str,
        data: sc.DataArray,
        size: sc.Variable | float = 1,
        artist_number: int = 0,
        opacity: float = 1,
    ):
        """
        Make a point cloud using pythreejs
        """
        import pythreejs as p3

        _check_ndim(data)
        self._canvas = canvas
        self._data = data
        self._x = x
        self._y = y
        self._z = z
        self._id = uuid.uuid4().hex
        self._artist_number = artist_number

        self._size = size
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
                        [self._data.coords[self._x].shape[0], 3], dtype='float32'
                    )
                ),
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

    def set_colors(self, rgba):
        """
        Set the point cloud's rgba colors:

        Parameters
        ----------
        rgba:
            The array of rgba colors.
        """
        self.geometry.attributes["color"].array = rgba[..., :3].astype('float32')

    def update(self, new_values):
        """
        Update point cloud array with new values.

        Parameters
        ----------
        new_values:
            New data to update the point cloud values from.
        """
        _check_ndim(new_values)
        self._data = new_values

    def get_limits(self) -> tuple[sc.Variable, sc.Variable, sc.Variable]:
        """
        Get the spatial extent of all the points in the cloud.
        """
        xcoord = self._data.coords[self._x]
        ycoord = self._data.coords[self._y]
        zcoord = self._data.coords[self._z]
        half_pixel = 0.5 * self._size
        dx = sc.scalar(half_pixel, unit=xcoord.unit)
        dy = sc.scalar(half_pixel, unit=ycoord.unit)
        dz = sc.scalar(half_pixel, unit=zcoord.unit)
        return (
            sc.concat([xcoord.min() - dx, xcoord.max() + dx], dim=self._x),
            sc.concat([ycoord.min() - dy, ycoord.max() + dy], dim=self._y),
            sc.concat([zcoord.min() - dz, zcoord.max() + dz], dim=self._z),
        )

    @property
    def opacity(self):
        """
        Get the material opacity.
        """
        return self.material.opacity

    @opacity.setter
    def opacity(self, val):
        """
        Set the material opacity.
        """
        self.material.opacity = val
        self.material.depthTest = val > 0.5

    @property
    def data(self):
        """
        Get the point cloud data.
        """
        return self._data

    def bbox(self, xscale: Literal['linear', 'log'], yscale: Literal['linear', 'log']):
        """
        The bounding box of the line.`
        """
        scatter_x = self._data.coords[self._x]
        scatter_y = self._data.coords[self._y]
        scatter_z = self._data.coords[self._z]
        return BoundingBox(
            **{**axis_bounds(('xmin', 'xmax'), scatter_x, xscale)},
            **{**axis_bounds(('ymin', 'ymax'), scatter_y, yscale)},
            **{**axis_bounds(('zmin', 'zmax'), scatter_z, yscale)},
        )

    def remove(self) -> None:
        """
        Remove the point cloud from the canvas.
        """
        self._canvas.remove(self.points)
