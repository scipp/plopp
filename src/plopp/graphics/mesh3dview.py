# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from typing import Literal, Optional, Tuple, Union

import scipp as sc

from .. import backends
from ..core import View
from ..core.utils import make_compatible
from ..graphics import Camera
from .colormapper import ColorMapper


class Mesh3dView(View):
    """
    View that makes a visual representation of three-dimensional mesh data.
    It has a :class:`Canvas`, a :class:`ColorMapper` and a specialized ``update``
    function that generates :class:`Mesh` artists.

    Parameters
    ----------
    *nodes:
        The nodes that are attached to the view.
    faces:
        The triangulated faced indexes that connect the vertices
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
    cmap:
        The name of the colormap for the data
        (see https://matplotlib.org/stable/tutorials/colors/colormaps.html).
        In addition to the Matplotlib docs, if the name is just a single html color,
        a colormap with that single color will be used.
    mask_cmap:
        The name of the colormap for masked data.
    norm:
        Control the scaling on the vertical axis.
    vmin:
        Lower bound for the colorbar. If a number (without a unit) is supplied, it is
        assumed that the unit is the same as the data unit.
    vmax:
        Upper bound for the colorbar. If a number (without a unit) is supplied, it is
        assumed that the unit is the same as the data unit.
    title:
        The figure title.
    figsize:
        The width and height of the figure, in pixels.
    camera:
        Initial camera configuration (position, target).
    **kwargs:
        All other kwargs are forwarded to the PointCloud artist.
    """

    def __init__(
        self,
        *nodes,
        faces: sc.DataArray | None = None,
        point: str | None = None,
        vertex: str = 'vertex',
        intensity: str = 'counts',
        face: str = 'face',
        triangle: str = 'triangle',
        cmap: str = 'viridis',
        mask_cmap: str = 'gray',
        norm: Literal['linear', 'log'] = 'linear',
        vmin: Optional[Union[sc.Variable, int, float]] = None,
        vmax: Optional[Union[sc.Variable, int, float]] = None,
        figsize: Tuple[int, int] = (600, 400),
        title: Optional[str] = None,
        camera: Optional[Camera] = None,
        **kwargs,
    ):
        super().__init__(*nodes)

        if faces is None:
            raise ValueError('The triangulated faces must be provided')

        self._bkargs = {'faces': faces, 'point': point, 'vertex': vertex, 'intensity': intensity,
                        'face': face, 'triangle': triangle}
        self._kwargs = kwargs

        self.canvas = backends.canvas3d(figsize=figsize, title=title, camera=camera)
        self.colormapper = ColorMapper(
            cmap=cmap,
            mask_cmap=mask_cmap,
            norm=norm,
            vmin=vmin,
            vmax=vmax,
            nan_color="#f0f0f0",
            figsize=self.canvas.figsize,
        )

        self._original_artists = [n.id for n in nodes]
        self.render()

    def update(self, new_values: sc.DataArray, key: str, draw=True):
        """
        Add new point cloud or update point cloud array with new values.

        Parameters
        ----------
        new_values:
            New data to create or update a :class:`PointCloud` object from.
        key:
            The id of the node that sent the new data.
        draw:
            This argument is ignored for the 3d figure update.
        """
        axes = ('x', 'y', 'z')
        intensity = self._bkargs['intensity']
        if self.canvas.empty:
            self.canvas.set_axes(
                dims={a: a for a in axes},
                units={a: new_values.data.unit for a in axes},
            )
            self.colormapper.unit = new_values.coords[intensity].unit
        else:
            new_values.coords[intensity] = make_compatible(
                new_values.coords[intensity], unit=self.colormapper.unit
            )
            # the data field is vector valued, so we only need to worry about x, y, or z
            new_values.data = new_values.data.to(unit=self.canvas.units['x'], copy=False)

        if key not in self.artists:
            pts = backends.mesh(data=new_values, **self._bkargs, **self._kwargs)
            self.artists[key] = pts
            self.colormapper[key] = pts  # inserts into self.colormapper.artists
            self.canvas.add(pts.points)
            if key in self._original_artists:
                self.canvas.make_outline(limits=self.get_limits())

        self.artists[key].update(new_values=new_values)
        self.colormapper.update(key=key, data=new_values)

    def get_limits(self) -> Tuple[sc.Variable, sc.Variable, sc.Variable]:
        """
        Get global limits for all the mesh clouds in the scene.
        """
        # use zip to go from a list of tuples to a tuple of lists, then make a dict
        axes = 'x', 'y', 'z'
        limits = {k: sc.concat(v, dim='children') for k, v in zip(
            axes, zip(*[child.get_limits() for child in self.artists.values()])
        )}

        def limit_pair(ax: str) -> sc.Variable:
            return sc.concat((sc.min(limits[ax]), sc.max(limits[ax])), dim=ax)

        return limit_pair(axes[0]), limit_pair(axes[1]), limit_pair(axes[2])

    def set_opacity(self, alpha: float):
        """
        Update the opacity of the original children (not the cuts).

        Parameters
        ----------
        alpha:
            The opacity value, between 0 and 1.
        """
        for name in self._original_artists:
            self.artists[name].opacity = alpha

    def remove(self, key: str):
        """
        Remove an object from the scene.

        Parameters
        ----------
        key:
            The id of the object to be removed.
        """
        self.canvas.remove(self.artists[key].points)
        del self.artists[key]
