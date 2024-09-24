# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

import uuid
from typing import Literal

import numpy as np
import scipp as sc
from matplotlib.colors import to_rgb

from ...core.limits import find_limits
from ...graphics.bbox import BoundingBox
from .canvas import Canvas


class Mesh3d:
    """
    Artist to represent a three-dimensional mesh.

    Parameters
    ----------
    canvas:
        The canvas to draw the mesh on.
    data:
        The initial data to create the mesh from. Must be a DataGroup that contains at
        least the following fields:

        - vertices: a DataArray with the vertices of the mesh.
        - faces: a DataArray with the faces of the mesh.
    color:
        The color of the mesh. If None, the mesh will be colored according to the
        artist number.
    opacity:
        The opacity of the mesh.
    edgecolor:
        The color of the edges of the mesh. If None, the edges will not be shown.
    artist_number:
        The number of the artist. This is used to determine the color of the mesh if
        `color` is None.
    """

    def __init__(
        self,
        *,
        canvas: Canvas,
        data: sc.DataArray,
        color: str | None = None,
        opacity: float = 1,
        edgecolor: str | None = None,
        artist_number: int = 0,
    ):
        import pythreejs as p3

        self._data = data
        self._canvas = canvas
        self._artist_number = artist_number
        self._id = uuid.uuid4().hex

        # Note: index *must* be unsigned!
        index = p3.BufferAttribute(
            array=self._data.coords["faces"]
            .value.values.flatten()
            .astype('uint32', copy=False)
        )

        pos = (
            self._data.coords["vertices"].values.astype('float32')
            if 'vertices' in self._data.coords
            else np.array(
                [
                    self._data.coords["x"].values.astype('float32', copy=False),
                    self._data.coords["y"].values.astype('float32', copy=False),
                    self._data.coords["z"].values.astype('float32', copy=False),
                ]
            ).T
        )
        attributes = {
            'position': p3.BufferAttribute(array=pos),
            'color': p3.BufferAttribute(
                array=np.broadcast_to(
                    np.array(to_rgb(f'C{artist_number}' if color is None else color)),
                    (self._data.coords["x"].shape[0], 3),
                ).astype('float32')
            ),
        }

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
        self._canvas.add(self.mesh)
        if self.edges is not None:
            self._canvas.add(self.edges)

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
        # TODO: for now we only update the data values of the artist.
        # Updating the positions of the vertices is doable but is made more complicated
        # by the edges geometry, whose positions cannot just be updated.
        # A new geometry and edge lines would have to be created, the old one removed
        # from the scene and the new one added.

    def bbox(
        self,
        xscale: Literal['linear', 'log'],
        yscale: Literal['linear', 'log'],
        zscale: Literal['linear', 'log'],
    ) -> BoundingBox:
        """
        The bounding box of the mesh.
        """
        coords = self._data.coords
        xbounds = find_limits(coords['x'], scale=xscale)
        ybounds = find_limits(coords['y'], scale=yscale)
        zbounds = find_limits(coords['z'], scale=zscale)
        return BoundingBox(
            xmin=xbounds[0].value,
            xmax=xbounds[1].value,
            ymin=ybounds[0].value,
            ymax=ybounds[1].value,
            zmin=zbounds[0].value,
            zmax=zbounds[1].value,
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
