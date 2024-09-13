# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

import uuid
from typing import Literal

import numpy as np
import scipp as sc

from ...core.limits import find_limits
from ...graphics.bbox import BoundingBox


class Mesh3d:
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

        self._data = data
        # self._data = None
        # if "vertexcolors" in self._dataset.coords:
        #     self._data = sc.DataArray(data=self._dataset["vertexcolors"])
        self._id = uuid.uuid4().hex

        position = p3.BufferAttribute(
            array=self._data.coords["vertices"].values.astype('float32', copy=False)
        )
        # Note: index *must* be unsigned!
        index = p3.BufferAttribute(
            array=self._data.coords["faces"]
            .value.values.flatten()
            .astype('uint32', copy=False)
        )

        attributes = {
            'position': position,
        }
        if "vertexcolors" in self._data.coords:
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
        self._data = new_values
        # if "vertexcolors" in self._dataset:
        #     self._data.data = self._dataset["vertexcolors"]
        # TODO: for now we only update the colors of the mesh. Updating the positions
        # of the vertices is doable but is made more complicated by the edges geometry,
        # whose positions cannot just be updated. A new geometry and edge lines would
        # have to be created, the old one removed from the scene and the new one added.

    def bbox(
        self,
        xscale: Literal['linear', 'log'],
        yscale: Literal['linear', 'log'],
        zscale: Literal['linear', 'log'],
    ) -> BoundingBox:
        """
        The bounding box of the mesh.
        """
        # xcoord = self._dataset["vertices"].fields.x
        # ycoord = self._dataset["vertices"].fields.y
        # zcoord = self._dataset["vertices"].fields.z
        verts = self._data.coords["vertices"]
        xbounds = find_limits(verts.fields.x, scale=xscale)
        ybounds = find_limits(verts.fields.y, scale=yscale)
        zbounds = find_limits(verts.fields.z, scale=zscale)
        return BoundingBox(
            xmin=xbounds[0].value,
            xmax=xbounds[1].value,
            ymin=ybounds[0].value,
            ymax=ybounds[1].value,
            zmin=zbounds[0].value,
            zmax=zbounds[1].value,
        )

        # return (
        #     sc.concat([xcoord.min(), xcoord.max()], dim='x'),
        #     sc.concat([ycoord.min(), ycoord.max()], dim='y'),
        #     sc.concat([zcoord.min(), zcoord.max()], dim='z'),
        # )

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