# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)


# from functools import partial

# from typing import Dict, Literal, Optional, Tuple, Union

# import scipp as sc

# from .. import backends
# from ..core import View
# from ..core.utils import make_compatible, name_with_unit
# from .colormapper import ColorMapper
# # from .view2d import View2d


# class ScatterView(View2d):
#     def __init__(
#         self,
#         *args,
#         x: str = 'x',
#         y: str = 'y',
#         color: Optional[
#             Union[Dict[str, Union[str, sc.Variable]], Union[str, sc.Variable]]
#         ] = None,
#         size: Optional[
#             Union[Dict[str, Union[str, sc.Variable]], Union[str, sc.Variable]]
#         ] = None,
#         **kwargs,
#     ):
#         self._illustrator = 'scatter'
#         self._x = x
#         self._y = y
#         super().__init__(*args, **kwargs)

#     def update(self, new_values: sc.DataArray, key: str):
#         if new_values.ndim != 1:
#             raise ValueError(f"ScatterView can only be used to plot 1-D data.")
#         xdim = self._x
#         ydim = self._y
#         super().update(new_values, key, xdim, ydim)


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
        color: Optional[
            Union[Dict[str, Union[str, sc.Variable]], Union[str, sc.Variable]]
        ] = None,
        size: Optional[
            Union[Dict[str, Union[str, sc.Variable]], Union[str, sc.Variable]]
        ] = None,
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
        cbar: bool = True,
        **kwargs
    ):
        super().__init__(*nodes)

        self._x = x
        self._y = y
        self._scale = {} if scale is None else scale
        self._mask_color = mask_color
        self._kwargs = kwargs
        self._repr_format = format
        self.canvas = backends.canvas2d(
            cbar=False,
            aspect=aspect,
            grid=grid,
            figsize=figsize,
            title=title,
            vmin=vmin,
            vmax=vmax,
            autoscale=autoscale,
            legend=legend,
            **kwargs
        )
        # if color is not None:
        #     if
        #     and not(isinstance(color,
        self.colormapper = ColorMapper(
            cmap=cmap,
            cbar=cbar,
            mask_cmap=mask_cmap,
            norm=norm,
            vmin=vmin,
            vmax=vmax,
            autoscale=autoscale,
            canvas=self.canvas,
        )

        self.render()
        self.canvas.autoscale()
        self.canvas.finalize()

    def update(self, new_values: sc.DataArray, key: str):
        """
        Add new line or update line values.

        Parameters
        ----------
        new_values:
            New data to create or update a :class:`Line` object from.
        key:
            The id of the node that sent the new data.
        """
        # if new_values.ndim != 1:
        #     raise ValueError("LineView can only be used to plot 1-D data.")
        mapping = {'x': self._x, 'y': self._y}
        xcoord = new_values.coords[self._x]
        ycoord = new_values.coords[self._y]
        if self.canvas.empty:
            self.canvas.set_axes(
                dims={'x': self._x, 'y': self._y},
                units={'x': xcoord.unit, 'y': ycoord.unit},
            )
            self.canvas.xlabel = name_with_unit(var=xcoord, name=self._x)
            self.canvas.ylabel = name_with_unit(var=ycoord, name=self._y)
            self.colormapper.unit = new_values.unit
            if self._x in self._scale:
                self.canvas.xscale = self._scale[self._x]
            if self._y in self._scale:
                self.canvas.yscale = self._scale[self._y]
        else:
            new_values.data = make_compatible(
                new_values.data, unit=self.colormapper.unit
            )
            for xy, dim in mapping.items():
                new_values.coords[dim] = new_values.coords[dim].to(
                    unit=self.canvas.units[xy], copy=False
                )
            # new_values.data = make_compatible(
            #     new_values.data, unit=self.colormapper.unit
            # )
            # for xyz, dim in {'x': self._x, 'y': self._y}.items():
            #     new_values.coords[dim] = make_compatible(
            #         new_values.coords[dim],
            #         dim=self.canvas.dims[xyz],
            #         unit=self.canvas.units[xyz],
            #     )

        if key not in self.artists:
            scatter = backends.scatter(
                canvas=self.canvas,
                data=new_values,
                number=len(self.artists),
                mask_color=self._mask_color,
                **self._kwargs
            )
            self.artists[key] = scatter
            self.colormapper[key] = scatter

        self.artists[key].update(new_values=new_values)
        # self.colormapper.update(key=key, data=new_values)
        self.canvas.autoscale()
