# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

from typing import Dict, Literal, Optional, Tuple, Union

import scipp as sc

from .. import backends
from ..core.typing import FigureLike
from .colormapper import ColorMapper
from .graphicalview import GraphicalView


class ScatterView(GraphicalView):
    """
    ScatterView that makes a visual representation of one-dimensional data as a
    scatter plot.
    It has a :class:`Canvas`, a :class:`ColorMapper` and a specialized ``update``
    function that generates :class:`Image` artists.

    .. versionadded:: 24.04.0

    Parameters
    ----------
    *nodes:
        The nodes that are attached to the view.
    x:
        The name of the coordinate to be used for the x-values.
    y:
        The name of the coordinate to be used for the y-values.
    size:
        The name of the coordinate to be used for the size of the markers.
    norm:
        Control the scaling on the vertical axis.
    vmin:
        Lower bound for the colorbar. If a number (without a unit) is supplied, it is
        assumed that the unit is the same as the data unit.
    vmax:
        Upper bound for the colorbar. If a number (without a unit) is supplied, it is
        assumed that the unit is the same as the data unit.
    autoscale:
        The behavior of the color range limits. If ``auto``, the limits automatically
        adjusts every time the data changes. If ``grow``, the limits are allowed to
        grow with time but they do not shrink. If ``False``, autoscale is disabled.
    scale:
        Control the scaling of the horizontal axis. For example, specify
        ``scale={'time': 'log'}`` if you want log-scale for the ``time`` dimension.
    mask_color:
        The color of the masks.
    aspect:
        Aspect ratio for the axes.
    grid:
        Show grid if ``True``.
    title:
        The figure title.
    figsize:
        The width and height of the figure, in inches.
    format:
        Format of the figure displayed in the Jupyter notebook. If ``None``, a SVG is
        created as long as the number of markers in the figure is not too large. If too
        many markers are drawn, a PNG image is created instead.
    legend:
        Show legend if ``True``. If ``legend`` is a tuple, it should contain the
        ``(x, y)`` coordinates of the legend's anchor point in axes coordinates.
    cmap:
        The name of the colormap for the data
        (see https://matplotlib.org/stable/tutorials/colors/colormaps.html).
        In addition to the Matplotlib docs, if the name is just a single html color,
        a colormap with that single color will be used.
    mask_cmap:
        The name of the colormap for masked data.
    cbar:
        Show colorbar if ``True``.
    **kwargs:
        All other kwargs are forwarded to the Scatter artist.
    """

    def __init__(
        self,
        *nodes,
        x: str = 'x',
        y: str = 'y',
        size: Optional[str] = None,
        norm: Literal['linear', 'log'] = 'linear',
        vmin: Optional[Union[sc.Variable, int, float]] = None,
        vmax: Optional[Union[sc.Variable, int, float]] = None,
        autoscale: Literal['auto', 'grow', False] = 'auto',
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


def scatterfigure(*args, **kwargs) -> FigureLike:
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
