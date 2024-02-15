# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import uuid
from typing import Tuple

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
    open_ended:
        Matches three.js CylinderGeometry openEnded -- cylinders are capped if False
    radial_segments:
        Matches three.sj CylinderGeometry radialSegments -- number of line segments used to approximate a circle
    twisted:
        Controls if 'height' faces are rectangular (False) or triangular (True)
    double_sided:
        Are the inner faces of the cylinder rendered?
    """

    def __init__(
            self,
            *,
            base: str,
            edge: str,
            far: str,
            data: sc.DataArray,
            opacity: float = 1,
            open_ended: bool = False,
            radial_segments: int = 6,
            twisted: bool = False,
            double_sided: bool = False,
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
        self._caps = not open_ended
        self._segments = radial_segments
        self._twist = twisted
        self._sides = double_sided
        self._id = uuid.uuid4().hex

        self.vertex_count, self.last_vertex, self.geometry = self.make_geometry()
        self.material = p3.PointsMaterial(
            vertexColors='FaceColors',
            transparent=True,
            opacity=opacity,
            side='DoubleSide' if self._sides else 'FrontSide',
        )
        self.points = p3.Mesh(geometry=self.geometry, material=self.material)

    def triangulate_all(self):
        """Combine all triangulations as scipp Variables, where possible"""
        from scipp import array, arange, flatten, transpose
        bases, edges, fars = (self._data.coords[name] for name in (self._base, self._edge, self._far))
        x = bases.dims[0]
        vertices, faces = triangulate(at=bases, to=fars, edge=edges, elements=self._segments, caps=self._caps, twist=self._twist)
        # vertices now has shape (cylinders, vertices), which we will flatten to only vertices
        # first we need to expand faces:
        count = vertices.sizes['vertices']
        first = arange(start=0, stop=bases.sizes[x], dim=x) * count
        faces = first + array(values=faces, dims=['faces', 'vertices'])
        return (flatten(transpose(vertices, dims=[x, 'vertices']), to='vertices'),
                flatten(transpose(faces, dims=[x,  'faces', 'vertices']), dims=[x, 'faces'], to='faces'),
                first + count, count)

    def make_geometry(self):
        """Construct the geometry from combined scipp Variables using the buffered index property"""
        from pythreejs import BufferGeometry, BufferAttribute
        from numpy import zeros
        v, faces, lasts, count = self.triangulate_all()
        position = BufferAttribute(array=v.values.astype('float32'))
        color = BufferAttribute(array=zeros([v.sizes['vertices'], 3], dtype='float32'))
        index = BufferAttribute(array=faces.values.flatten().astype('uint32'))  # *MUST* be unsigned!
        return count, lasts, BufferGeometry(index=index, attributes={'position': position, 'color': color})

    def set_colors(self, rgba):
        """
        Set the cylinders cloud's rgba colors:

        Parameters
        ----------
        rgba:
            The array of rgba colors.
        """
        from scipp import array, transpose, flatten, ones
        if rgba.shape[0] != len(self.last_vertex):
            raise ValueError(f"Wrong number of colors ({rgba.shape[0]}) to set for cylinders {len(self.last_vertex)}")
        colors = array(values=rgba[:, :3], dims=['cylinder', 'rgb']) * ones(shape=[self.vertex_count], dims=['vertex'])
        colors = flatten(transpose(colors, dims=['cylinder', 'vertex', 'rgb']), dims=['cylinder', 'vertex'], to='v')
        self.geometry.attributes['color'].array = colors.values.astype('float32')

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
        # vertices, faces, normals, lasts = self.triangulate_all()
        vertices, faces, lasts, count = self.triangulate_all()
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
                elements: int = 6, rings: int = 1, unit: str | None = None, caps: bool = True,
                twist: bool = True):
    from scipp import sqrt, dot, arange, concat, flatten, fold, vectors, cross, Variable
    from scipp.spatial import rotations_from_rotvecs
    from numpy import array, tile
    if unit is None:
        unit = at.unit or 'm'

    l_vec = to.to(unit=unit) - at.to(unit=unit)
    ll = sqrt(dot(l_vec, l_vec))
    # *a* vector perpendicular to l (should we check that this _is_ perpendicular to l_vec?)
    p = edge.to(unit=unit) - at.to(unit=unit)

    # arange does _not_ include the stop value, by design
    a = arange(start=0., stop=360., step=360/elements, dim='ring', unit='degree')
    temp_dim = uuid.uuid4().hex
    full_a = a * l_vec / ll
    ring = fold(rotations_from_rotvecs(flatten(full_a, dims=full_a.dims, to=temp_dim)), dim=temp_dim, sizes=full_a.sizes) * p
    li = at.to(unit=unit) + arange(start=0, stop=rings + 1, dim='length') * l_vec / rings
    if twist:
        # twists = Variable(values=tile(array([0, 180/elements]), (rings + 1) // 2), dims=['length'], unit='degree')
        twists = arange(start=0., stop=rings+1, step=1, dim='length', unit='degree') * (-180 / elements)
        full_t = twists * l_vec / ll
        r_twist = fold(rotations_from_rotvecs(flatten(full_t, dims=full_t.dims, to=temp_dim)), dim=temp_dim, sizes=full_t.sizes)
        ring = r_twist * ring

    vertices = flatten(li + ring, dims=['length', 'ring'], to='vertices')  # the order in the addition is important
    if caps:
        # 0, elements*[0,elements), elements*elements + 1
        vertices = concat((at.to(unit=unit), vertices, to.to(unit=unit)), 'vertices')
    faces = []
    if caps:
        # bottom cap
        faces = [[0, (i + 1) % elements + 1, i + 1] for i in range(elements)]
    # between rings
    for j in range(rings):
        z = 1 + j * elements if caps else j * elements
        rf = [[[z + i, z + (i + 1) % elements, z + (i + 1) % elements + elements],
               [z + i, z + (i + 1) % elements + elements, z + i + elements]] for i in range(elements)]
        faces.extend([triangle for triangles in rf for triangle in triangles])
    if caps:
        # top cap
        last = len(vertices) - 1
        top = [[last, last - (i + 1) % elements - 1, last - i - 1] for i in range(elements)]
        faces.extend(top)
    faces = array(faces, dtype=int)
    return vertices, faces

