# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

from typing import Dict, Literal, Optional, Tuple, Union

import scipp as sc

from .. import backends
from .colormapper import ColorMapper
from .graphicalview import GraphicalView


class ScatterView(GraphicalView):
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

        self._dims = {'x': x, 'y': y}
        self._ndim = 1
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
        self.canvas.finalize()

    def make_artist(self, new_values):
        return backends.scatter(
            canvas=self.canvas,
            data=new_values,
            x=self._dims['x'],
            y=self._dims['y'],
            size=self._size,
            number=len(self.artists),
            mask_color=self._mask_color,
            cbar=self._cbar,
            **self._kwargs,
        )


def scatterfigure(*args, **kwargs):
    """
    Create a figure to represent scatter data from one or more graph node(s).

    .. versionadded:: 24.04.0

    Examples
    --------
    Create an input node and attach a ``scatterfigure`` as a view:

      >>> da = pp.data.scatter()
      >>> in_node = pp.Node(da)
      >>> fig = pp.scatterfigure(in_node)

    A scatter figure with a color bar (using the data values for the color scale):

      >>> da = pp.data.scatter()
      >>> in_node = pp.Node(da)
      >>> fig = pp.scatterfigure(in_node, cbar=True)
    """

    return backends.figure2d(ScatterView, *args, **kwargs)
