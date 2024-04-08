# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from typing import Dict, Literal, Optional, Tuple, Union

import scipp as sc

from .. import backends
from .colormapper import ColorMapper
from .graphicalview import GraphicalView


class ImageView(GraphicalView):
    """
    ImageView that makes a visual representation of two-dimensional data.
    It has a :class:`Canvas`, a :class:`ColorMapper` and a specialized ``update``
    function that generates :class:`Image` artists.

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
    autoscale:
        The behavior of the color range limits. If ``auto``, the limits automatically
        adjusts every time the data changes. If ``grow``, the limits are allowed to
        grow with time but they do not shrink.
    scale:
        Control the scaling of the horizontal axis. For example, specify
        ``scale={'tof': 'log'}`` if you want log-scale for the ``tof`` dimension.
    aspect:
        Aspect ratio for the axes.
    grid:
        Show grid if ``True``.
    cbar:
        Show colorbar if ``True``.
    title:
        The figure title.
    figsize:
        The width and height of the figure, in inches.
    ax:
        If supplied, use these axes to create the figure. If none are supplied, the
        canvas will create its own axes.
    cax:
        If supplied, use these axes for the colorbar. If none are supplied, and a
        colorbar is required, the canvas will create its own axes.
    format:
        Format of the figure displayed in the Jupyter notebook. If ``None``, a SVG is
        created as long as the number of markers in the figure is not too large. If too
        many markers are drawn, a PNG image is created instead.
    **kwargs:
        All other kwargs are forwarded to the Image artist.
    """

    def __init__(
        self,
        *nodes,
        cmap: str = 'viridis',
        mask_cmap: str = 'gray',
        norm: Literal['linear', 'log'] = 'linear',
        vmin: Optional[Union[sc.Variable, int, float]] = None,
        vmax: Optional[Union[sc.Variable, int, float]] = None,
        autoscale: Literal['auto', 'grow'] = 'auto',
        scale: Optional[Dict[str, str]] = None,
        aspect: Literal['auto', 'equal'] = 'auto',
        grid: bool = False,
        cbar: bool = True,
        title: Optional[str] = None,
        figsize: Optional[Tuple[float, float]] = None,
        format: Optional[Literal['svg', 'png']] = None,
        **kwargs,
    ):
        super().__init__(*nodes)

        # Note: the order of dims matters here, reversing it would transpose the image
        self._dims = {'y': None, 'x': None}
        self._ndim = 2
        self._scale = {} if scale is None else scale
        self._kwargs = kwargs
        self._repr_format = format
        self.canvas = backends.canvas2d(
            cbar=cbar, aspect=aspect, grid=grid, title=title, figsize=figsize, **kwargs
        )
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

    def make_artist(self, new_values):
        return backends.image(canvas=self.canvas, data=new_values, **self._kwargs)


def imagefigure(*args, **kwargs):
    """
    Create a figure to represent two-dimensional data from one or more graph node(s).

    .. versionadded:: 24.04.0
    """

    return backends.figure2d(ImageView, *args, **kwargs)
