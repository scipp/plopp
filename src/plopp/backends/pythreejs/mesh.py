# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

import uuid

import numpy as np
import scipp as sc


class Mesh:
    """
    Artist to represent a three-dimensional mesh.

    Parameters
    ----------
    data:
        The initial data to create the mesh from. Must be a DataGroup that contains at
        least the following fields:
        - vertices: a DataArray with the vertices of the mesh.
        - faces: a DataArray with the faces of the mesh.
    opacity:
        The opacity of the mesh.
    edgecolor:
        The color of the edges of the mesh. If None, the edges will not be shown.
    """

    def __init__(
        self,
        *,
        data: sc.DataArray,
        opacity: float = 1,
        edgecolor: str | None = None,
    ):
        import pythreejs as p3

        self._datagroup = data
        self._data = None
        if "vertexcolors" in self._datagroup:
            self._data = sc.DataArray(data=self._datagroup["vertexcolors"])
        self._id = uuid.uuid4().hex

        position = p3.BufferAttribute(
            array=self._datagroup["vertices"].values.astype('float32', copy=False)
        )
        # Note: index *must* be unsigned!
        index = p3.BufferAttribute(
            array=self._datagroup["faces"].values.flatten().astype('uint32', copy=False)
        )

        attributes = {
            'position': position,
        }
        if self._data is not None:
            attributes["color"] = p3.BufferAttribute(
                array=np.zeros((len(self._data), 3), dtype='float32')
            )

        self.geometry = p3.BufferGeometry(index=index, attributes=attributes)
        self.material = p3.MeshBasicMaterial(
            vertexColors='VertexColors',
            transparent=True,
            side='DoubleSide',
            opacity=opacity,
            depthTest=opacity > 0.5,
        )
        self.mesh = p3.Mesh(geometry=self.geometry, material=self.material)
        self.edges = (
            p3.LineSegments(
                p3.EdgesGeometry(self.geometry),
                p3.LineBasicMaterial(
                    color=edgecolor or 'black',
                    linewidth=2,
                    opacity=opacity,
                    transparent=True,
                ),
            )
            if edgecolor is not None
            else None
        )

    def set_colors(self, rgba):
        """
        Set the mesh's rgba colors:

        Parameters
        ----------
        rgba:
            The array of rgba colors.
        """
        self.geometry.attributes["color"].array = rgba[..., :3].astype(
            'float32', copy=False
        )

    def update(self, new_values):
        """
        Update mesh array with new values.

        Parameters
        ----------
        new_values:
            New data to update the mesh values from.
        """
        self._datagroup = new_values
        if "vertexcolors" in self._datagroup:
            self._data.data = self._datagroup["vertexcolors"]
        # TODO: for now we only update the colors of the mesh. Updating the positions
        # of the vertices is doable but is made more complicated by the edges geometry,
        # whose positions cannot just be updated. A new geometry and edge lines would
        # have to be created, the old one removed from the scene and the new one added.

    def get_limits(self) -> tuple[sc.Variable, sc.Variable, sc.Variable]:
        """
        Get the spatial extent of all the points in the cloud.
        """
        xcoord = self._datagroup["vertices"].fields.x
        ycoord = self._datagroup["vertices"].fields.y
        zcoord = self._datagroup["vertices"].fields.z
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
