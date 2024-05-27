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
    """
    View that makes a visual representation of three-dimensional mesh data.
    It has a :class:`Canvas`, a :class:`ColorMapper` and a specialized ``update``
    function that generates :class:`Mesh` artists.

    Parameters
    ----------
    *nodes:
        The nodes that are attached to the view.
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
    figsize:
        The width and height of the figure, in pixels.
    title:
        The figure title.
    camera:
        Initial camera configuration (position, target).
    """

    def __init__(
        self,
        *nodes,
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
        new_colors = {
            key: sc.DataArray(data=values["vertexcolors"])
            for key, values in new.items()
            if "vertexcolors" in values
        }
        for key, new_values in new.items():
            if self.canvas.empty:
                self.canvas.set_axes(
                    dims=None,
                    units={"vertices": new_values["vertices"].unit},
                    dtypes=None,
                )
                color = new_colors.get(key, None)
                self.colormapper.unit = color.unit if color is not None else None
            else:
                if key in new_colors:
                    new_colors[key].data = make_compatible(
                        new_colors[key].data, unit=self.colormapper.unit
                    )
                new_values["vertices"] = make_compatible(
                    new_values["vertices"], unit=self.canvas.units["vertices"]
                )

            if key not in self.artists:
                mesh = backends.mesh(data=new_values, **self._kwargs)
                self.artists[key] = mesh
                self.colormapper[key] = mesh
                self.canvas.add(mesh.mesh)
                self.canvas.add(mesh.edges)
                if key in self._original_artists:
                    self.canvas.make_outline(limits=self.get_limits())

            self.artists[key].update(new_values=new_values)
        self.colormapper.update(
            **{
                key: sc.DataArray(data=values["vertexcolors"])
                for key, values in new.items()
                if "vertexcolors" in values
            }
        )

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
    """
    Create a 3D mesh figure.

    .. versionadded:: 24.06.0
    """

    return backends.figure3d(Mesh3dView, *args, **kwargs)
