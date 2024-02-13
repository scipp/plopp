# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import uuid
from typing import Tuple, Union

import numpy as np
import scipp as sc


def _check_ndim(data):
    if data.ndim != 1:
        raise ValueError(
            'Cylinders only accepts one dimensional data, '
            f'found {data.ndim} dimensions. You should flatten your data '
            '(using scipp.flatten) before sending it to the cylinders viewer.'
        )


class Cylinders:
    """
    Artist to represent a three-dimensional plot of intensity on cylinders.

    Parameters
    ----------
    x:
        The name of the coordinate that is to be used for the X positions.
    y:
        The name of the coordinate that is to be used for the Y positions.
    z:
        The name of the coordinate that is to be used for the Z positions.
    base:
        The name of the coordinate that is to be used for the cylinder basal face index
    edge:
        The name of the coordinate that is to be used for the cylinder edge index
    far:
        The name of the coordinate that is to be used for the cylinder far face index
    data:
        The initial data to create the line from.
    opacity:
        The opacity of the points.
    """

    def __init__(
        self,
        *,
        x: str,
        y: str,
        z: str,
        base: str,
        edge: str,
        far: str,
        data: sc.DataArray,
        opacity: float = 1,
    ):
        """
        Make a point cloud using pythreejs
        """
        import pythreejs as p3

        _check_ndim(data)
        self._data = data
        self._x = x
        self._y = y
        self._z = z
        self._base = base
        self._edge = edge
        self._far = far
        self._id = uuid.uuid4().hex

        self.geometry = self.make_geometry()
        self.material = p3.PointsMaterial(
            vertexColors='VertexColors',
            transparent=True,
            opacity=opacity,
        )
        p3geometry = p3.Group()
        p3geometry.add(self.geometry)
        self.points = p3.Points(geometry=p3geometry, material=self.material)

    def make_geometry(self):
        from pythreejs import BufferGeometry, CylinderGeometry
        from math import sqrt
        from numpy import zeros
        x = self._data.coords[self._x].values.astype('float32')
        y = self._data.coords[self._y].values.astype('float32')
        z = self._data.coords[self._z].values.astype('float32')
        cylinders = []
        for base, edge, far in zip(self._base, self._edge, self._far):
            bx, by, bz = x[base], y[base], z[base]
            ex, ey, ez = x[edge] - bx, y[edge] - by, z[edge] - bz
            # We _could_ check that e-vec is perpendicular to c-vec -- but skip that for now
            cx, cy, cz = (x[far] - bx) / 2, (y[far] - by) / 2, (z[far] - bz) / 2
            r = sqrt(ex * ex + ey * ey + ez * ez)
            half = sqrt(cx * cx + cy * cy + cz * cz)
            cyl = BufferGeometry.from_geometry(CylinderGeometry(radiusTop=r, radiusBottom=r, height=2*half))
            cyl.applyQuaternion(yhat_to_vector_p3_quaternion(cx, cy, cz, half))
            cyl.attributes['position'].array += (cx, cy, cz)
            cyl.attributes['color'] = zeros([cyl.attributes['position'].array.shape[0], 3], dtype='float32')
            cylinders.append(cyl)
        return cylinders

    def set_colors(self, rgba):
        """
        Set the cylinders cloud's rgba colors:

        Parameters
        ----------
        rgba:
            The array of rgba colors.
        """
        if rgba.shape[0] != len(self.geometry):
            raise ValueError(f"Wrong number of colors ({rgba.shape[0]}) to set for cylinders {len(self.geometry)}")

        for i, cyl in enumerate(self.geometry):
            cyl.attribtes['color'].array[:] = rgba[i, :3].astype('float32')

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

    def get_limits(self) -> Tuple[sc.Variable, sc.Variable, sc.Variable]:
        """
        Get the spatial extent of all the cylinders.
        """
        # A more correct form of this would project the cylinders onto each axis
        xcoord = self._data.coords[self._x]
        ycoord = self._data.coords[self._y]
        zcoord = self._data.coords[self._z]
        return (
            sc.concat([xcoord.min(), xcoord.max()], dim=self._x),
            sc.concat([ycoord.min(), ycoord.max()], dim=self._y),
            sc.concat([zcoord.min(), zcoord.max()], dim=self._z),
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


def yhat_to_vector_p3_quaternion(x, y, z, length):
    from numpy import sqrt, dot, cross
    from pythreejs import Quaternion
    # following http://lolengine.net/blog/2013/09/18/beautiful-maths-quaternion-from-vectors
    u = 0, 1, 0
    v = x / length, y / length, z / length
    scalar_part = 0.5 * sqrt(2 + 2 * dot(u, v))
    vector_part = 0.5 * cross(u, v) / scalar_part
    return Quaternion(x=vector_part[0], y=vector_part[1], z=vector_part[2], w=scalar_part)
