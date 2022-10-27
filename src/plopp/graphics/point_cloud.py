# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core.limits import find_limits, fix_empty_range

import numpy as np
import scipp as sc
from typing import Tuple


class PointCloud:
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
    pixel_size:
        The size of the markers.
    opacity:
        The opacity of the points.
    """

    def __init__(
            self,
            *,
            x: str,
            y: str,
            z: str,
            data: sc.DataArray,
            pixel_size: float = 1,  # TODO: pixel_size should have units
            opacity: float = 1):
        """
        Make a point cloud using pythreejs
        """
        import pythreejs as p3

        self._data = data
        self._x = x
        self._y = y
        self._z = z

        self.geometry = p3.BufferGeometry(
            attributes={
                'position':
                p3.BufferAttribute(array=np.array([
                    self._data.meta[self._x].values.astype('float32'), self._data.meta[
                        self._y].values.astype('float32'), self._data.meta[
                            self._z].values.astype('float32')
                ]).T),
                'color':
                p3.BufferAttribute(array=np.zeros(
                    [self._data.meta[self._x].shape[0], 3], dtype='float32'))
            })

        # TODO: a device pixel_ratio should probably be read from a config file
        pixel_ratio = 1.0
        # Note that an additional factor of 2.5 (obtained from trial and error) seems to
        # be required to get the sizes right in the scene.
        self.material = p3.PointsMaterial(vertexColors='VertexColors',
                                          size=2.5 * pixel_size * pixel_ratio,
                                          transparent=True,
                                          opacity=opacity)
        self.points = p3.Points(geometry=self.geometry, material=self.material)

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
        self._data = new_values

    def get_limits(self) -> Tuple[sc.Variable, sc.Variable, sc.Variable]:
        """
        Get the spatial extent of all the points in the cloud.
        """
        xmin, xmax = fix_empty_range(find_limits(self._data.meta[self._x]))
        ymin, ymax = fix_empty_range(find_limits(self._data.meta[self._y]))
        zmin, zmax = fix_empty_range(find_limits(self._data.meta[self._z]))
        return (sc.concat([xmin, xmax],
                          dim=self._x), sc.concat([ymin, ymax], dim=self._y),
                sc.concat([zmin, zmax], dim=self._z))

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
