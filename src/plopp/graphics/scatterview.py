# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

from typing import Dict, Literal, Optional, Tuple, Union

import scipp as sc

from .. import backends
from ..core import View
from ..core.utils import make_compatible, name_with_unit
from .colormapper import ColorMapper


class ScatterView(View):
    """ """

    def __init__(
        self,
        *nodes,
        x: str = 'x',
        y: str = 'y',
        size: Optional[str] = None,
        norm: Literal['linear', 'log'] = 'linear',
        vmin: Optional[Union[sc.Variable, int, float]] = None,
        vmax: Optional[Union[sc.Variable, int, float]] = None,
        autoscale: Literal['auto', 'grow'] = 'auto',
        scale: Optional[Dict[str, str]] = None,
        mask_color: str = 'black',
        aspect: Literal['auto', 'equal'] = 'auto',
        grid: bool = False,
        title: Optional[str] = None,
        figsize: Tuple[float, float] = None,
        format: Optional[Literal['svg', 'png']] = None,
        legend: Union[bool, Tuple[float, float]] = True,
        cmap: str = 'viridis',
        mask_cmap: str = 'gray',
        cbar: bool = False,
        **kwargs,
    ):
        super().__init__(*nodes)

        self._x = x
        self._y = y
        self._size = size
        self._cbar = cbar
        self._scale = {} if scale is None else scale
        self._mask_color = mask_color
        self._kwargs = kwargs
        self._repr_format = format
        self.canvas = backends.canvas2d(
            cbar=self._cbar,
            aspect=aspect,
            grid=grid,
            figsize=figsize,
            title=title,
            vmin=vmin,
            vmax=vmax,
            autoscale=autoscale,
            legend=legend,
            **kwargs,
        )
        if self._cbar:
            self.colormapper = ColorMapper(
                cmap=cmap,
                cbar=True,
                mask_cmap=mask_cmap,
                norm=norm,
                vmin=vmin,
                vmax=vmax,
                autoscale=autoscale,
                canvas=self.canvas,
            )
        else:
            self.colormapper = None

        self.render()
        self.canvas.autoscale()
        self.canvas.finalize()

    def update(self, args=None, **kwargs):
        """
        Add new line or update line values.

        Parameters
        ----------
        new_values:
            New data to create or update a :class:`Line` object from.
        key:
            The id of the node that sent the new data.
        """
        new = kwargs
        if args is not None:
            new.update(args)
        for key, new_values in new.items():
            xcoord = new_values.coords[self._x]
            ycoord = new_values.coords[self._y]
            if self.canvas.empty:
                self.canvas.set_axes(
                    dims={'x': self._x, 'y': self._y},
                    units={'x': xcoord.unit, 'y': ycoord.unit},
                )
                self.canvas.xlabel = name_with_unit(var=xcoord, name=self._x)
                self.canvas.ylabel = name_with_unit(var=ycoord, name=self._y)
                if self.colormapper is not None:
                    self.colormapper.unit = new_values.unit
                if self._x in self._scale:
                    self.canvas.xscale = self._scale[self._x]
                if self._y in self._scale:
                    self.canvas.yscale = self._scale[self._y]
            else:
                if self.colormapper is not None:
                    new_values.data = make_compatible(
                        new_values.data, unit=self.colormapper.unit
                    )
                for xy, dim in {'x': self._x, 'y': self._y}.items():
                    new_values.coords[dim] = make_compatible(
                        new_values.coords[dim],
                        unit=self.canvas.units[xy],
                    )

            if key not in self.artists:
                scatter = backends.scatter(
                    canvas=self.canvas,
                    data=new_values,
                    x=self._x,
                    y=self._y,
                    size=self._size,
                    number=len(self.artists),
                    mask_color=self._mask_color,
                    cbar=self._cbar,
                    **self._kwargs,
                )
                self.artists[key] = scatter
                if self.colormapper is not None:
                    self.colormapper[key] = scatter

            self.artists[key].update(new_values=new_values)

        if self.colormapper is not None:
            self.colormapper.update(args, **kwargs)
        self.canvas.autoscale()
