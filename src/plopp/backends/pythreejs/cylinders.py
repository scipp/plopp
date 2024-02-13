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
        self._base = base
        self._edge = edge
        self._far = far
        self._id = uuid.uuid4().hex

        self.last_vertex, self.geometry = self.make_geometry()
        self.material = p3.PointsMaterial(
            vertexColors='VertexColors',
            transparent=True,
            opacity=opacity,
        )
        self.points = p3.MeshBasicMaterial(geometry=self.geometry, material=self.material)

    def make_geometry(self):
        from pythreejs import BufferGeometry, BufferAttribute
        from numpy import zeros, ndarray, vstack, array
        bases, edges, fars = (self._data.coords[name] for name in (self._base, self._edge, self._far))

        # this should really all be assembled into a single geometry, with face indexes offset...
        cylinders = []
        all_vertices = ndarray([0, 3], dtype='float32')
        all_faces = ndarray([0, 3], dtype='int32')
        last_vertex = []
        for base, edge, far in zip(bases, edges, fars):
            vertices, faces = triangulate(at=base, to=far, edge=edge)
            offset = all_vertices.shape[0]
            all_vertices = vstack((all_vertices, vertices.values.astype('float32')))
            all_faces = vstack((all_faces, offset + array(faces, dtype='int32')))
            last_vertex.append(all_vertices.shape[0])

        return last_vertex, BufferGeometry(attributes={
            'position': BufferAttribute(array=all_vertices),
            'faces': BufferAttribute(array=all_faces),
            'color': BufferAttribute(zeros([all_vertices.shape[0], 3], dtype='float32')),
        })

    def set_colors(self, rgba):
        """
        Set the cylinders cloud's rgba colors:

        Parameters
        ----------
        rgba:
            The array of rgba colors.
        """
        if rgba.shape[0] != len(self.last_vertex):
            raise ValueError(f"Wrong number of colors ({rgba.shape[0]}) to set for cylinders {len(self.last_vertex)}")

        first = 0
        for i, last in enumerate(self.last_vertex):
            self.geometry.attributes['color'].array[first:last, :] = rgba[i, :3].astype('float32')
            first = last

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
        from scipp import concat
        coords = self._data.coords
        # A more correct form of this would project the cylinders onto each axis
        vertices = concat([coords[self._base], coords[self._edge], coords[self._far]], dim=self._base)
        xcoord = vertices.fields.x
        ycoord = vertices.fields.y
        zcoord = vertices.fields.z
        return (
            sc.concat([xcoord.min(), xcoord.max()], dim=self._base),
            sc.concat([ycoord.min(), ycoord.max()], dim=self._base),
            sc.concat([zcoord.min(), zcoord.max()], dim=self._base),
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


def yhat_to_vector_quaternion(x, y, z, length):
    from numpy import sqrt, dot, cross
    # following http://lolengine.net/blog/2013/09/18/beautiful-maths-quaternion-from-vectors
    # now access restricted, but accessible via the web archive
    # https://web.archive.org/web/20220120192932/http://lolengine.net/blog/2013/09/18/beautiful-maths-quaternion-from-vectors
    u = 0, 1, 0
    v = x / length, y / length, z / length
    scalar_part = 0.5 * sqrt(2 + 2 * dot(u, v))
    vector_part = 0.5 * cross(u, v) / scalar_part
    return scalar_part, vector_part


def yhat_to_vector_rotation(x, y, z, length):
    r, (i, j, k) = yhat_to_vector_quaternion(x, y, z, length)
    s = 1 / (r * r + i * i + j * j + k * k)
    return [[1 - 2 * s * (j * j + k * k), 2 * s * (i * j - k * r), 2 * s * (i * k + j * r)],
            [2 * s * (i * j + k * r), 1 - 2 * s * (i * i + k * k), 2 * s * (j * k - i * r)],
            [2 * s * (i * k - j * r), 2 * s * (j * k + i * r), 1 - 2 * s * (i * i + j * j)]]


def triangulate(*, at: sc.Variable, to: sc.Variable, edge: sc.Variable, elements: int = 1, unit: str|None = None):
    from scipp import vector, vectors, sqrt, dot, isclose, cross, scalar, arange, concat, flatten
    from scipp.spatial import rotations_from_rotvecs
    if unit is None:
        unit = at.unit or 'm'
    l_vec = to.to(unit=unit) - at.to(unit=unit)
    ll = sqrt(dot(l_vec, l_vec))
    # *a* vector perpendicular to l (should we check that this _is_ perpendicular to l_vec?)
    p = edge.to(unit=unit) - at.to(unit=unit)

    a = arange(start=0, stop=360, step=30, dim='ring', unit='degree')
    r = rotations_from_rotvecs(a * l_vec / ll)

    nvr = len(a)  # the number of vertices per ring
    ring = r * p
    li = at.to(unit=unit) + arange(start=0, stop=elements + 1, dim='length') * l_vec / elements
    vertices = flatten(li + ring, to='vertices')  # the order in the addition is important for flatten
    # 0, elements*[0,nvr), elements*nvr + 1
    vertices = concat((at.to(unit=unit), vertices, to.to(unit=unit)), 'vertices')
    # bottom cap
    faces = [[0, i + 1, (i + 1) % nvr + 1] for i in range(nvr)]
    # between rings
    for j in range(elements):
        z = 1 + j * nvr
        rf = [[[z + i, z + (i + 1) % nvr, z + (i + 1) % nvr + nvr],
               [z + i, z + (i + 1) % nvr + nvr, z + i + nvr]] for i in range(nvr)]
        faces.extend([triangle for triangles in rf for triangle in triangles])
    # top cap
    last = len(vertices) - 1
    top = [[last, last - i - 1, last - (i + 1) % nvr - 1] for i in range(nvr)]
    faces.extend(top)
    return vertices, faces
