# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

import uuid
from typing import Tuple
from enum import Enum, auto

import scipp as sc


class Mesh:
    class IntensityType(Enum):
        vertex = auto()
        point = auto()
        every = auto()

    def _check_intensity_type(self, data: sc.DataArray) -> IntensityType:
        """Ensure the intensity type provided in `data` is useable by this function and return its type"""
        if self._intensity not in data.coords:
            raise ValueError(
                f'Mesh expected to contain intensity along coordinate {self._intensity}, '
                f'but instead contains coordinates {list(data.coords.keys())}'
            )
        # The intensity coordinate _must_ be (point_dim,), (vertex_dim,) _or_ (point_dim, vertex_dim)
        # for it to fit into a DataArray coordinate for data. We only expect the first case, but maybe
        # the other two cases are useful too?
        if self._point is None:
            self._point = [x for x in data.dims if x != self._vertex][0]
        intensity = data.coords[self._intensity]
        if intensity.ndim == 2 and all(x in intensity.dims for x in (self._point, self._vertex)):
            return self.IntensityType.every
        if intensity.ndim == 1 and any(x == intensity.dim for x in (self._point, self._vertex)):
            return self.IntensityType.point if intensity.dim == self._point else self.IntensityType.vertex
        # If we were passed a non-viable data array we could end up here, so throw an error
        raise ValueError(
            f'Mesh intensity coordinate dimensions not {(self._point,)}, {(self._vertex,)}, '
            f'or {(self._point, self._vertex)}, but {intensity.dims}  instead'
        )

    def _check_data_dims(self, data: sc.DataArray):
        if data.ndim != 2:
            raise ValueError(
                'Mesh only accepts two dimensional data, '
                f'found {data.ndim} dimensions. You should reshape your data '
                '(e.g., using scipp.flatten) before sending it to the mesh viewer.'
            )
        if self._vertex not in data.dims:
            raise ValueError(
                f'Mesh expected to contain data along the vertex dimension {self._vertex}'
                f' but instead has only {data.dims}.'
            )
        if (t := self._check_intensity_type(data)) != self._type:
            raise ValueError(f'Mesh intensity type expected to match {self._type} but is {t}')
        return data

    def _check_face_dims(self, faces: sc.Variable):
        """Ensure that the provided face indexing makes sense"""
        if faces.ndim == 1:
            if faces.dim != self._triangle or faces.sizes[self._triangle] != 3:
                raise ValueError('Mesh triangulation must contain at least one triangle')
            faces = faces.fold(dim=self._triangle, sizes={self._face: 1, self._triangle: 3})

        if faces.ndim != 2:
            raise ValueError(f'Mesh triangulation expected to be 2-dimensional but has {self._faces.ndim} dimensions')

        if any(x not in faces.dims for x in (self._face, self._triangle)):
            raise ValueError(
                f'Mesh triangulation expected to have dims {(self._face, self._triangle)} but has {faces.dims}'
            )
        if faces.sizes[self._triangle] != 3:
            raise ValueError(
                f'Mesh triangulation expected 3 indexes per face but provided {faces.sizes[self._triangle]}'
            )
        return faces

    """
    Artist to represent a three-dimensional plot of intensity on a regular triangulated mesh.

    Parameters
    ----------
    point:
        The name of the point dimension in the data (will be determined if None)
    vertex:
        The name of the vertex dimension in data (default = 'vertex')
    intensity:
        The name of the intensity coordinate to plot (default = 'counts')
    face:
        The name of the face dimension in faces (default = 'face')
    triangle:
        The name of the triangle dimension in faces (default = 'triangle')
    data:
        The initial data to create the mesh from -- data == (N,M) vertices, coords={`intensity`: (N,)})
    faces:
        The triangulated face index list that applies to all mesh polyhedra
    opacity:
        The opacity of the points.
    double_sided:
        Are the inner faces of the polyhedra rendered?
    """

    def __init__(
            self,
            *,
            data: sc.DataArray,
            faces: sc.Variable,
            opacity: float = 1,
            double_sided: bool = False,
            point: str | None = None,
            vertex: str = 'vertex',
            intensity: str = 'counts',
            face: str = 'face',
            triangle: str = 'triangle',
    ):
        """
        Make a point cloud using pythreejs
        """
        import pythreejs as p3
        self._point = point
        self._vertex = vertex
        self._intensity = intensity
        self._face = face
        self._triangle = triangle

        self._type = self._check_intensity_type(data)
        self._data = self._check_data_dims(data)
        self._faces = self._check_face_dims(faces)

        self._id = uuid.uuid4().hex

        self.vertex_count, self.last_vertex, self.geometry = self.make_geometry()
        self.material = p3.MeshBasicMaterial(
            vertexColors='VertexColors',
            transparent=True,
            opacity=opacity,
            side='DoubleSide' if double_sided else 'FrontSide',
        )
        self.points = p3.Mesh(geometry=self.geometry, material=self.material)

    def make_geometry(self):
        """Construct the geometry from combined scipp Variables using the buffered index property"""
        from pythreejs import BufferGeometry, BufferAttribute
        from numpy import zeros
        from scipp import arange
        # ensuring the vertex dimension is first keeps the vertices-per-point contiguous after flattening
        vertices = self._data.data.transpose(dims=[self._point, self._vertex]).flatten(to='vertices')
        # The _first_ vertex index for each polyhedron in the list of all vertices
        first = arange(start=0, stop=self._data.sizes[self._point], dim=self._point) * self._data.sizes[self._vertex]
        # The face indexes need to be scaled-up to the full vertex list
        faces = (first + self._faces).transpose(dims=[self._point, self._face, self._triangle]).flatten(to='vertices')
        #
        last = first + self._data.sizes[self._vertex]
        count = self._data.sizes[self._vertex]

        position = BufferAttribute(array=vertices.values.astype('float32'))
        color = BufferAttribute(array=zeros([count, 3], dtype='float32'))
        index = BufferAttribute(array=faces.values.flatten().astype('uint32'))  # *MUST* be unsigned!
        return count, last, BufferGeometry(index=index, attributes={'position': position, 'color': color})

    def set_colors(self, rgba):
        """
        Set the mesh's rgba colors:

        Parameters
        ----------
        rgba:
            The array of rgba colors.
        """
        from scipp import array, transpose, flatten, ones
        if self.IntensityType.every == self._type:
            if (no := len(self.last_vertex) * self.vertex_count) != rgba.shape[0]:
                raise ValueError(f"Wrong number of colors {rgba.shape[0]} to set for all {no} vertices")
            colors = rgba[:, :3]
        elif self.IntensityType.point == self._type:
            if (no := len(self.last_vertex)) != rgba.shape[0]:
                raise ValueError(f"Wrong number of colors ({rgba.shape[0]}) to set for {no} polyhedra")
            colors = array(values=rgba[:, :3], dims=['p', 'rgb']) * ones(shape=[self.vertex_count], dims=['vertex'])
            colors = colors.transpose(dims=['p', 'vertex', 'rgb']).flatten(dims=['p', 'vertex'], to='v').values
        elif self.IntensityType.vertex == self._type:
            if (no := self.vertex_count) != rgba.shape[0]:
                raise ValueError(f"Wrong number of colors ({rgba.shape[0]}) to set for {no} vertices")
            colors = array(values=rgba[:, :3], dims=['vertex', 'rgb']) * ones(shape=[len(self.last_vertex)], dims=['p'])
            colors = flatten(transpose(colors, dims=['p', 'vertex', 'rgb']), dims=['p', 'vertex'], to='v').values
        else:
            raise ValueError(f'Impossible IntensityType {self._type}')
        self.geometry.attributes['color'].array = colors.astype('float32')

    def update(self, new_values):
        """
        Update mesh array with new values.

        Warning
        -------
        This method _is_ called when a mesh is _first_ drawn, and can therefore make debugging changes in
        the make_geometry() method challenging.

        Parameters
        ----------
        new_values:
            New data to update the mesh values from.
        """
        self._data = self._check_data_dims(new_values)
        # plus update the vertex positions (should we check that they've actually changed?)
        vertices = self._data.data.transpose(dims=[self._point, self._vertex]).flatten(to='vertices')
        self.geometry.attributes['position'].array = vertices.values.astype('float32')

    def get_limits(self) -> Tuple[sc.Variable, sc.Variable, sc.Variable]:
        """
        Get the spatial extent of all the cylinders.
        """
        # A more correct form of this would project the cylinders onto each axis
        # vertices, faces, normals, lasts = self.triangulate_all()
        return (
            sc.concat([self._data.data.fields.x.min(), self._data.data.fields.x.max()], dim='x'),
            sc.concat([self._data.data.fields.y.min(), self._data.data.fields.y.max()], dim='y'),
            sc.concat([self._data.data.fields.z.min(), self._data.data.fields.z.max()], dim='z'),
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
        Get the mesh _intensity_ data.

        Used by plopp.ColorMapper._set_artists_colors to map plot-data into
        color range, then passed back to this class' set_colors method.
        """
        return sc.DataArray(data=self._data.coords[self._intensity], masks=self._data.masks)

    @property
    def raw_data(self):
        """
        Get the mesh _intensity_ data

        Used by plopp.ColorMapper.autoscale to set the color-axis limits
        """
        return self.data


