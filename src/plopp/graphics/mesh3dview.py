# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from typing import Literal

import scipp as sc

from .. import backends
from ..core import View
from ..core.typing import FigureLike
from ..core.utils import make_compatible
from .camera import Camera
from .colormapper import ColorMapper


class Mesh3dView(View):
    """ """

    def __init__(
        self,
        *nodes,
        vertices: str = 'vertices',
        faces: str = 'faces',
        cmap: str = 'viridis',
        mask_cmap: str = 'gray',
        norm: Literal['linear', 'log'] = 'linear',
        vmin: sc.Variable | float | None = None,
        vmax: sc.Variable | float | None = None,
        figsize: tuple[int, int] = (600, 400),
        title: str | None = None,
        camera: Camera | None = None,
        **kwargs,
    ):
        super().__init__(*nodes)

        self._vertices = vertices
        self._faces = faces
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

    def update(self, *args, **kwargs):
        """
        Update the view with new meshes by either supplying a dictionary of
        new data or by keyword arguments.
        """
        new = dict(*args, **kwargs)
        # mapping = {'x': self._x, 'y': self._y, 'z': self._z}
        print('new', new)
        for key, new_values in new.items():
            print('new_values', new_values)
            # if self.canvas.empty:
            #     self.canvas.set_axes(
            #         dims=mapping,
            #         units={
            #             x: new_values.coords[dim].unit for x, dim in mapping.items()
            #         },
            #         dtypes={
            #             x: new_values.coords[dim].dtype for x, dim in mapping.items()
            #         },
            #     )
            #     self.colormapper.unit = new_values.unit
            # else:
            #     new_values.data = make_compatible(
            #         new_values.data, unit=self.colormapper.unit
            #     )
            #     for xyz, dim in mapping.items():
            #         new_values.coords[dim] = new_values.coords[dim].to(
            #             unit=self.canvas.units[xyz], copy=False
            #         )

            if key not in self.artists:
                mesh = backends.mesh(
                    data=new_values,
                    vertices=self._vertices,
                    faces=self._faces,
                    **self._kwargs,
                )
                self.artists[key] = mesh
                self.colormapper[key] = mesh
                self.canvas.add(mesh.mesh)
                if key in self._original_artists:
                    self.canvas.make_outline(limits=self.get_limits())

            self.artists[key].update(new_values=new_values)
        # self.colormapper.update(**new)

    def get_limits(self) -> tuple[sc.Variable, sc.Variable, sc.Variable]:
        """
        Get global limits for all the point clouds in the scene.
        """
        xmin = None
        xmax = None
        ymin = None
        ymax = None
        zmin = None
        zmax = None
        for child in self.artists.values():
            xlims, ylims, zlims = child.get_limits()
            if xmin is None or xlims[0] < xmin:
                xmin = xlims[0]
            if xmax is None or xlims[1] > xmax:
                xmax = xlims[1]
            if ymin is None or ylims[0] < ymin:
                ymin = ylims[0]
            if ymax is None or ylims[1] > ymax:
                ymax = ylims[1]
            if zmin is None or zlims[0] < zmin:
                zmin = zlims[0]
            if zmax is None or zlims[1] > zmax:
                zmax = zlims[1]
        return (
            sc.concat([xmin, xmax], dim='x'),
            sc.concat([ymin, ymax], dim='y'),
            sc.concat([zmin, zmax], dim='z'),
        )

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


def mesh3dfigure(*args, **kwargs) -> FigureLike:
    """ """

    return backends.figure3d(Mesh3dView, *args, **kwargs)
