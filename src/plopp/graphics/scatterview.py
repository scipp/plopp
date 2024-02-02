# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)


from functools import partial

from typing import Dict, Literal, Optional, Tuple, Union

import scipp as sc

# from .. import backends
# from ..core import View
# from ..core.utils import make_compatible, name_with_unit
# from .colormapper import ColorMapper
from .view2d import View2d


class ScatterView(View2d):
    def __init__(
        self,
        *args,
        x: str = 'x',
        y: str = 'y',
        color: Optional[
            Union[Dict[str, Union[str, sc.Variable]], Union[str, sc.Variable]]
        ] = None,
        size: Optional[
            Union[Dict[str, Union[str, sc.Variable]], Union[str, sc.Variable]]
        ] = None,
        **kwargs,
    ):
        self._illustrator = 'scatter'
        self._x = x
        self._y = y
        super().__init__(*args, **kwargs)

    def update(self, new_values: sc.DataArray, key: str):
        if new_values.ndim != 1:
            raise ValueError(f"ScatterView can only be used to plot 1-D data.")
        xdim = self._x
        ydim = self._y
        super().update(new_values, key, xdim, ydim)


# from typing import Dict, Literal, Optional, Tuple, Union

# import scipp as sc

# from .. import backends
# from ..core import View
# from ..core.utils import make_compatible, name_with_unit


# class ScatterView(View):
#     """ """

#     def __init__(
#         self,
#         *nodes,
#         x: str = 'x',
#         y: str = 'y',
#         color: Optional[
#         Union[Dict[str, Union[str, sc.Variable]], Union[str, sc.Variable]]
#     ] = None,
#     size: Optional[
#         Union[Dict[str, Union[str, sc.Variable]], Union[str, sc.Variable]]
#     ] = None,
#         norm: Literal['linear', 'log'] = 'linear',
#         vmin: Optional[Union[sc.Variable, int, float]] = None,
#         vmax: Optional[Union[sc.Variable, int, float]] = None,
#         autoscale: Literal['auto', 'grow'] = 'auto',
#         scale: Optional[Dict[str, str]] = None,
#         mask_color: str = 'black',
#         aspect: Literal['auto', 'equal'] = 'auto',
#         grid: bool = False,
#         title: Optional[str] = None,
#         figsize: Tuple[float, float] = None,
#         format: Optional[Literal['svg', 'png']] = None,
#         legend: Union[bool, Tuple[float, float]] = True,
#         **kwargs
#     ):
#         super().__init__(*nodes)

#         self._scale = {} if scale is None else scale
#         self._mask_color = mask_color
#         self._kwargs = kwargs
#         self._repr_format = format
#         self.canvas = backends.canvas2d(
#             cbar=False,
#             aspect=aspect,
#             grid=grid,
#             figsize=figsize,
#             title=title,
#             vmin=vmin,
#             vmax=vmax,
#             autoscale=autoscale,
#             legend=legend,
#             **kwargs
#         )
#         if color is not None:
#             if
#             and not(isinstance(color,
#         self.colormapper = ColorMapper(
#             cmap=cmap,
#             cbar=cbar,
#             mask_cmap=mask_cmap,
#             norm=norm,
#             vmin=vmin,
#             vmax=vmax,
#             autoscale=autoscale,
#             canvas=self.canvas,
#         )

#         self.render()
#         self.canvas.autoscale()
#         self.canvas.finalize()

#     def update(self, new_values: sc.DataArray, key: str):
#         """
#         Add new line or update line values.

#         Parameters
#         ----------
#         new_values:
#             New data to create or update a :class:`Line` object from.
#         key:
#             The id of the node that sent the new data.
#         """
#         if new_values.ndim != 1:
#             raise ValueError("LineView can only be used to plot 1-D data.")

#         xdim = new_values.dim
#         xcoord = new_values.coords[xdim]
#         if self.canvas.empty:
#             self.canvas.set_axes(
#                 dims={'x': xdim}, units={'x': xcoord.unit, 'y': new_values.unit}
#             )
#             self.canvas.xlabel = name_with_unit(var=xcoord)
#             self.canvas.ylabel = name_with_unit(var=new_values.data, name="")
#             if xdim in self._scale:
#                 self.canvas.xscale = self._scale[xdim]
#         else:
#             new_values.data = make_compatible(
#                 new_values.data, unit=self.canvas.units['y']
#             )
#             new_values.coords[xdim] = make_compatible(
#                 xcoord, dim=self.canvas.dims['x'], unit=self.canvas.units['x']
#             )

#         if key not in self.artists:
#             line = backends.line(
#                 canvas=self.canvas,
#                 data=new_values,
#                 number=len(self.artists),
#                 errorbars=self._errorbars,
#                 mask_color=self._mask_color,
#                 **self._kwargs
#             )
#             self.artists[key] = line

#         else:
#             self.artists[key].update(new_values=new_values)

#         self.canvas.autoscale()
