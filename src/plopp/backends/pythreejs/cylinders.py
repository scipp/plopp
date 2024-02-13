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
            vertexColors='FaceColors',
            transparent=True,
            opacity=opacity,
        )
        self.points = p3.Mesh(geometry=self.geometry, material=self.material)

    def triangulate_all(self):
        """Combine all triangulations as scipp Variables, where possible"""
        from scipp import concat
        from numpy import vstack
        bases, edges, fars = (self._data.coords[name] for name in (self._base, self._edge, self._far))
        vertices = []
        faces = []
        normals = []
        last = [0,]
        for base, edge, far in zip(bases, edges, fars):
            v, f, n = triangulate(at=base, to=far, edge=edge)
            vertices.append(v)
            faces.append(f + last[-1])
            normals.append(n)
            last.append(last[-1] + v.shape[0])

        return concat(vertices, dim='vertices'), vstack(faces), concat(normals, dim='vertices'), last[1:]

    def make_geometry(self):
        """Construct the geometry from combined scipp Variables using the buffered index property"""
        from pythreejs import BufferGeometry, BufferAttribute
        from numpy import zeros, array
        v, faces, n, lasts = self.triangulate_all()
        position = BufferAttribute(array=v.values.astype('float32'))
        normal = BufferAttribute(array=n.values.astype('float32'))
        color = BufferAttribute(array=zeros([lasts[-1], 3], dtype='float32'))
        index = BufferAttribute(array=array(faces).flatten().astype('uint32'))  # *MUST* be unsigned!
        return lasts, BufferGeometry(index=index, attributes={'position': position, 'normal': normal, 'color': color})

    def set_colors(self, rgba):
        """
        Set the cylinders cloud's rgba colors:

        Parameters
        ----------
        rgba:
            The array of rgba colors.
        """
        from numpy import tile, diff, vstack
        if rgba.shape[0] != len(self.last_vertex):
            raise ValueError(f"Wrong number of colors ({rgba.shape[0]}) to set for cylinders {len(self.last_vertex)}")
        counts = diff([0,] + self.last_vertex)
        color = vstack([tile(rgba[i, :3], (n, 1)) for i, n in enumerate(counts)])
        self.geometry.attributes['color'].array = color.astype('float32')

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
        vertices, faces, normals, lasts = self.triangulate_all()
        return (
            sc.concat([vertices.fields.x.min(), vertices.fields.x.max()], dim='x'),
            sc.concat([vertices.fields.y.min(), vertices.fields.y.max()], dim='y'),
            sc.concat([vertices.fields.z.min(), vertices.fields.z.max()], dim='z'),
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


def triangulate(*, at: sc.Variable, to: sc.Variable, edge: sc.Variable,
                elements: int = 5, rings: int = 1, unit: str | None = None, caps: bool = True):
    from scipp import sqrt, dot, arange, concat, flatten, vectors, cross
    from scipp.spatial import rotations_from_rotvecs
    from numpy import array
    if unit is None:
        unit = at.unit or 'm'
    l_vec = to.to(unit=unit) - at.to(unit=unit)
    ll = sqrt(dot(l_vec, l_vec))
    # *a* vector perpendicular to l (should we check that this _is_ perpendicular to l_vec?)
    p = edge.to(unit=unit) - at.to(unit=unit)

    # arange does _not_ include the stop value, by design
    a = arange(start=0., stop=360., step=360/elements, dim='ring', unit='degree')
    r = rotations_from_rotvecs(a * l_vec / ll)

    # nvr = len(a)  # the number of vertices per ring
    nvr = elements
    ring = r * p
    li = at.to(unit=unit) + arange(start=0, stop=rings + 1, dim='length') * l_vec / rings
    vertices = flatten(li + ring, to='vertices')  # the order in the addition is important for flatten
    if caps:
        # 0, elements*[0,nvr), elements*nvr + 1
        vertices = concat((at.to(unit=unit), vertices, to.to(unit=unit)), 'vertices')
    faces = []
    if caps:
        # bottom cap
        faces = [[0, (i + 1) % nvr + 1, i + 1] for i in range(nvr)]
    # between rings
    for j in range(rings):
        z = 1 + j * nvr
        rf = [[[z + i, z + (i + 1) % nvr, z + (i + 1) % nvr + nvr],
               [z + i, z + (i + 1) % nvr + nvr, z + i + nvr]] for i in range(nvr)]
        faces.extend([triangle for triangles in rf for triangle in triangles])
    if caps:
        # top cap
        last = len(vertices) - 1
        top = [[last, last - (i + 1) % nvr - 1, last - i - 1] for i in range(nvr)]
        faces.extend(top)
    faces = array(faces, dtype=int)
    va = vectors(values=vertices.values[faces[:, 1]] - vertices.values[faces[:, 0]], dims=['vertices'])
    vb = vectors(values=vertices.values[faces[:, 2]] - vertices.values[faces[:, 1]], dims=['vertices'])
    normals = cross(va, vb)
    normals /= sqrt(dot(normals, normals))
    return vertices, faces, normals
