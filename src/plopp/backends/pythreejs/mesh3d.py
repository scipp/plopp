# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

import uuid
from typing import Literal

import numpy as np
import scipp as sc
from matplotlib.colors import to_rgb

from ...core.limits import find_limits
from ...graphics.bbox import BoundingBox
from ...graphics.colormapper import ColorMapper
from .canvas import Canvas


class Mesh3d:
    """
    Artist to represent a three-dimensional mesh.

    .. versionadded:: 24.09.2

    Parameters
    ----------
    canvas:
        The canvas to draw the mesh on.
    data:
        The initial data to create the mesh from. Must be a DataGroup that contains at
        least the following fields:

        - vertices: a DataArray with the vertices of the mesh.
        - faces: a DataArray with the faces of the mesh.
    uid:
        The unique identifier of the artist. If None, a random UUID is generated.
    color:
        The color of the mesh. If None, the mesh will be colored according to the
        artist number.
    colormapper:
        The colormapper to use for the mesh.
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
        uid: str | None = None,
        color: str | None = None,
        colormapper: ColorMapper | None = None,
        opacity: float = 1,
        edgecolor: str | None = None,
        artist_number: int = 0,
    ):
        import pythreejs as p3

        self.uid = uid if uid is not None else uuid.uuid4().hex
        self._data = data
        self._canvas = canvas
        self._colormapper = colormapper
        self._artist_number = artist_number

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

        if self._colormapper is not None:
            self._colormapper.add_artist(self.uid, self)
            colors = self._colormapper.rgba(self.data)[..., :3].astype('float32')
        else:
            colors = np.broadcast_to(
                np.array(to_rgb(f'C{artist_number}' if color is None else color)),
                (self._data.coords["x"].shape[0], 3),
            ).astype('float32')

        attributes = {
            'position': p3.BufferAttribute(array=pos),
            'color': p3.BufferAttribute(array=colors),
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

    def notify_artist(self, message: str) -> None:
        """
        Receive notification from the colormapper that its state has changed.
        We thus need to update the colors of the points.

        Parameters
        ----------
        message:
            The message from the colormapper.
        """
        self._update_colors()

    def _update_colors(self):
        """
        Set the point cloud's rgba colors:
        """
        self.geometry.attributes["color"].array = self._colormapper.rgba(self.data)[
            ..., :3
        ].astype('float32')

    def update(self, new_values):
        """
        Update mesh array with new values.

        Parameters
        ----------
        new_values:
            New data to update the mesh values from.
        """
        self._data = new_values
        if self._colormapper is not None:
            self._update_colors()
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
    def opacity(self) -> float:
        """
        The mesh opacity.
        """
        return self.material.opacity

    @opacity.setter
    def opacity(self, val: float):
        self.material.opacity = val
        if self.edges is not None:
            self.edges.material.opacity = val
        self.material.depthTest = val > 0.5

    @property
    def visible(self) -> bool:
        """
        The visibility of the mesh.
        """
        return self.mesh.visible

    @visible.setter
    def visible(self, val: bool):
        self.mesh.visible = val
        if self.edges is not None:
            self.edges.visible = val

    @property
    def data(self):
        """
        Get the mesh data.
        """
        return self._data

    def remove(self) -> None:
        """
        Remove the mesh from the canvas.
        """
        self._canvas.remove(self.points)
        if self._colormapper is not None:
            self._colormapper.remove_artist(self.uid)
