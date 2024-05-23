# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import uuid

import numpy as np
import scipp as sc


class Mesh:
    """ """

    def __init__(
        self,
        *,
        vertices: str,
        faces: str,
        # color: str,
        data: sc.DataArray,
        opacity: float = 1,
    ):
        """ """
        import pythreejs as p3

        self._data = data
        self._vertices = vertices
        self._faces = faces
        # self._color = color
        self._id = uuid.uuid4().hex

        position = p3.BufferAttribute(
            array=self._data[self._vertices].values.astype('float32')
        )
        # color = p3.BufferAttribute(array=np.random.random([4, 3]).astype('float32'))
        index = p3.BufferAttribute(
            array=self._data[self._faces].values.flatten().astype('uint32')
        )  # *MUST* be unsigned!

        self.geometry = p3.BufferGeometry(
            index=index,
            attributes={
                'position': position,
                #  'color': color
            },
        )

        self.material = p3.MeshBasicMaterial(
            vertexColors='VertexColors', transparent=True, side='DoubleSide'
        )
        self.mesh = p3.Mesh(geometry=self.geometry, material=self.material)

    def set_colors(self, rgba):
        """
        Set the mesh's rgba colors:

        Parameters
        ----------
        rgba:
            The array of rgba colors.
        """
        self.geometry.attributes["color"].array = rgba[..., :3].astype('float32')

    def update(self, new_values):
        """
        Update mesh array with new values.

        Parameters
        ----------
        new_values:
            New data to update the mesh values from.
        """
        # _check_ndim(new_values)
        self._data = new_values

    def get_limits(self) -> tuple[sc.Variable, sc.Variable, sc.Variable]:
        """
        Get the spatial extent of all the points in the cloud.
        """
        xcoord = self._data[self._vertices].fields.x
        ycoord = self._data[self._vertices].fields.y
        zcoord = self._data[self._vertices].fields.z
        return (
            sc.concat([xcoord.min(), xcoord.max()], dim='x'),
            sc.concat([ycoord.min(), ycoord.max()], dim='y'),
            sc.concat([zcoord.min(), zcoord.max()], dim='z'),
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
        Get the mesh data.
        """
        return self._data
