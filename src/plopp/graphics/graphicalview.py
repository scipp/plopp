# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

from collections.abc import Callable
from typing import Any, Literal

import numpy as np
import scipp as sc

from ..core import Node, View
from ..core.typing import CanvasLike
from ..core.utils import make_compatible, name_with_unit
from .bbox import BoundingBox
from .camera import Camera
from .colormapper import ColorMapper


def _none_if_not_finite(x: float | None) -> float | int | None:
    if x is None:
        return None
    return x if np.isfinite(x) else None


class GraphicalView(View):
    """
    Base class for graphical 1d and 2d views.
    It is used to represent line plots, scatter plots, and image plots (heatmaps).
    In addition to ``View``, it updates the canvas axes and labels when new data is
    supplied.
    It also verifies that the new data supplied is compatible with the existing axes
    dimensions and units.
    """

    def __init__(
        self,
        *nodes: Node,
        dims: dict[str, str | None],
        canvas_maker: CanvasLike,
        artist_maker: Callable,
        colormapper: bool = False,
        cmap: str = 'viridis',
        mask_cmap: str = 'gray',
        cbar: bool = False,
        norm: Literal['linear', 'log'] = 'linear',
        vmin: sc.Variable | float | None = None,
        vmax: sc.Variable | float | None = None,
        autoscale: Literal['auto', 'grow'] = 'auto',
        scale: dict[str, str] | None = None,
        aspect: Literal['auto', 'equal'] = 'auto',
        grid: bool = False,
        title: str | None = None,
        figsize: tuple[float, float] | None = None,
        format: Literal['svg', 'png'] | None = None,
        legend: bool | tuple[float, float] = False,
        camera: Camera | None = None,
        ax: Any = None,
        cax: Any = None,
        **kwargs,
    ):
        super().__init__(*nodes)
        self._dims = dims
        self._scale = {} if scale is None else scale
        self.artists = {}
        self._artist_maker = artist_maker
        self._kwargs = kwargs
        self._repr_format = format
        self._autoscale = autoscale
        self._bbox = BoundingBox()

        self.canvas = canvas_maker(
            cbar=cbar,
            aspect=aspect,
            grid=grid,
            figsize=figsize,
            title=title,
            vmin=vmin,
            vmax=vmax,
            legend=legend,
            camera=camera,
            ax=ax,
            cax=cax,
        )

        self.colormapper = (
            ColorMapper(
                cmap=cmap,
                cbar=cbar,
                mask_cmap=mask_cmap,
                norm=norm,
                vmin=vmin,
                vmax=vmax,
                autoscale=autoscale,
                canvas=self.canvas,
                figsize=getattr(self.canvas, "figsize", None),
            )
            if colormapper
            else None
        )

        if len(self._dims) == 1:
            self.canvas.yscale = norm
        self.render()

    def autoscale(self):
        bbox = BoundingBox()
        scales = {"xscale": self.canvas.xscale, "yscale": self.canvas.yscale}
        if hasattr(self.canvas, 'zscale'):
            scales['zscale'] = self.canvas.zscale
        for artist in self.artists.values():
            bbox = bbox.union(artist.bbox(**scales))
        self._bbox = self._bbox.union(bbox) if self._autoscale == 'grow' else bbox
        self._bbox = self._bbox.override(self.canvas.bbox)
        self.canvas.xrange = (
            _none_if_not_finite(self._bbox.xmin),
            _none_if_not_finite(self._bbox.xmax),
        )
        self.canvas.yrange = (
            _none_if_not_finite(self._bbox.ymin),
            _none_if_not_finite(self._bbox.ymax),
        )
        if hasattr(self.canvas, 'zrange'):
            self.canvas.zrange = (
                _none_if_not_finite(self._bbox.zmin),
                _none_if_not_finite(self._bbox.zmax),
            )
        self.canvas.draw()

    def update(self, *args, **kwargs) -> None:
        """
        Update the view with new data by either supplying a dictionary of
        new data or by keyword arguments.
        """
        new = dict(*args, **kwargs)
        for key, new_values in new.items():
            coords = {}
            for i, direction in enumerate(self._dims):
                if self._dims[direction] is None:
                    self._dims[direction] = new_values.dims[i]
                try:
                    coords[direction] = new_values.coords[self._dims[direction]]
                except KeyError as e:
                    raise KeyError(
                        "Supplied data is incompatible with this view: "
                        f"coordinate '{self._dims[direction]}' was not found in data."
                    ) from e

            if self.canvas.empty:
                axes_units = {k: coord.unit for k, coord in coords.items()}
                axes_dtypes = {k: coord.dtype for k, coord in coords.items()}
                if 'y' in self._dims:
                    self.canvas.ylabel = name_with_unit(
                        var=coords['y'], name=self._dims['y']
                    )
                    if self._dims['y'] in self._scale:
                        self.canvas.yscale = self._scale[self._dims['y']]
                else:
                    self.canvas.ylabel = name_with_unit(var=new_values.data, name="")
                    axes_units['y'] = new_values.unit
                    axes_dtypes['y'] = new_values.dtype

                self.canvas.set_axes(
                    dims=self._dims, units=axes_units, dtypes=axes_dtypes
                )
                self.canvas.xlabel = name_with_unit(
                    var=coords['x'], name=self._dims['x']
                )
                if self.colormapper is not None:
                    self.colormapper.unit = new_values.unit
                if self._dims['x'] in self._scale:
                    self.canvas.xscale = self._scale[self._dims['x']]
            else:
                if self.colormapper is not None:
                    new_values.data = make_compatible(
                        new_values.data, unit=self.colormapper.unit
                    )
                for xy, dim in self._dims.items():
                    new_values.coords[dim] = make_compatible(
                        coords[xy], unit=self.canvas.units[xy]
                    )
                if 'y' not in self._dims:
                    new_values.data = make_compatible(
                        new_values.data, unit=self.canvas.units['y']
                    )

            if key not in self.artists:
                self.artists[key] = self._artist_maker(
                    canvas=self.canvas,
                    data=new_values,
                    artist_number=len(self.artists),
                    **self._kwargs,
                )

                if self.colormapper is not None:
                    self.colormapper[key] = self.artists[key]

            self.artists[key].update(new_values=new_values)

        if self.colormapper is not None:
            self.colormapper.update(**new)
        self.autoscale()

    def remove(self, key: str) -> None:
        """
        Remove an object from the scene.

        Parameters
        ----------
        key:
            The id of the object to be removed.
        """
        self.artists[key].remove()
        del self.artists[key]
        self.autoscale()
