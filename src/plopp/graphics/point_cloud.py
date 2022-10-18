# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core.limits import find_limits, fix_empty_range

import numpy as np
import scipp as sc


class PointCloud:

    def __init__(
            self,
            *,
            x,
            y,
            z,
            data,
            pixel_size=1,  # TODO: pixel_size should have units
            opacity=1):
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
        self.geometry.attributes["color"].array = rgba[..., :3].astype('float32')

    def update(self, new_values):
        self._data = new_values

    def get_limits(self):
        xmin, xmax = fix_empty_range(find_limits(self._data.meta[self._x]))
        ymin, ymax = fix_empty_range(find_limits(self._data.meta[self._y]))
        zmin, zmax = fix_empty_range(find_limits(self._data.meta[self._z]))
        return (sc.concat([xmin, xmax],
                          dim=self._x), sc.concat([ymin, ymax], dim=self._y),
                sc.concat([zmin, zmax], dim=self._z))

    @property
    def opacity(self):
        return self.material.opacity

    @opacity.setter
    def opacity(self, val):
        self.material.opacity = val
        self.material.depthTest = val > 0.5

    @property
    def data(self):
        return self._data
