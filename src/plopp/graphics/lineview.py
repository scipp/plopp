# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from typing import Literal

import scipp as sc

from .. import backends
from ..core.typing import FigureLike
from .graphicalview import GraphicalView


class LineView(GraphicalView):
    """
    View that makes a visual representation of one-dimensional data.
    It has a :class:`Canvas` and a specialized ``update`` function that generates
    :class:`Line` artists.

    Parameters
    ----------
    *nodes:
        The nodes that are attached to the view.
    norm:
        Control the scaling on the vertical axis.
    vmin:
        Lower bound for the vertical axis. If a number (without a unit) is supplied,
        it is assumed that the unit is the same as the current vertical axis unit.
    vmax:
        Upper bound for the vertical axis. If a number (without a unit) is supplied,
        it is assumed that the unit is the same as the current vertical axis unit.
    autoscale:
        The behavior of the axis limits. If ``auto``, the limits automatically
        adjusts every time the data changes. If ``grow``, the limits are allowed to
        grow with time but they do not shrink.
    scale:
        Control the scaling of the horizontal axis. For example, specify
        ``scale={'tof': 'log'}`` if you want log-scale for the ``tof`` dimension.
    errorbars:
        Hide errorbars if ``False``.
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
    ax:
        If supplied, use these axes to create the figure. If none are supplied, the
        canvas will create its own axes.
    format:
        Format of the figure displayed in the Jupyter notebook. If ``None``, a SVG is
        created as long as the number of markers in the figure is not too large. If too
        many markers are drawn, a PNG image is created instead.
    legend:
        Show legend if ``True``. If ``legend`` is a tuple, it should contain the
        ``(x, y)`` coordinates of the legend's anchor point in axes coordinates.
    **kwargs:
        All other kwargs are forwarded to Matplotlib:

        - ``matplotlib.pyplot.plot`` for 1d data with a non bin-edge coordinate
        - ``matplotlib.pyplot.step`` for 1d data with a bin-edge coordinate
    """

    def __init__(
        self,
        *nodes,
        norm: Literal['linear', 'log'] = 'linear',
        vmin: sc.Variable | float | None = None,
        vmax: sc.Variable | float | None = None,
        autoscale: Literal['auto', 'grow'] = 'auto',
        scale: dict[str, str] | None = None,
        errorbars: bool = True,
        mask_color: str = 'black',
        aspect: Literal['auto', 'equal'] = 'auto',
        grid: bool = False,
        title: str | None = None,
        figsize: tuple[float, float] | None = None,
        format: Literal['svg', 'png'] | None = None,
        legend: bool | tuple[float, float] = True,
        **kwargs,
    ):
        super().__init__(*nodes)

        self._dims = {'x': None}
        self._ndim = 1
        self._scale = {} if scale is None else scale
        self._errorbars = errorbars
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
            **kwargs,
        )
        self.canvas.yscale = norm
        self.render()
        self.canvas.finalize()

    def make_artist(self, new_values):
        return backends.line(
            canvas=self.canvas,
            data=new_values,
            number=len(self.artists),
            errorbars=self._errorbars,
            mask_color=self._mask_color,
            **self._kwargs,
        )


def linefigure(*args, **kwargs) -> FigureLike:
    """
    Create a figure to represent one-dimensional data from one or more graph node(s).

    .. versionadded:: 24.04.0

    Examples
    --------
    Create an input node and attach a ``linefigure`` as a view:

      >>> da = pp.data.data1d()
      >>> in_node = pp.Node(da)
      >>> fig = pp.linefigure(in_node)

    Visualize two data arrays on the same figure:

      >>> a = pp.data.data1d()
      >>> b = 3 * a
      >>> a_node = pp.Node(a)
      >>> b_node = pp.Node(b)
      >>> fig = pp.linefigure(a_node, b_node)

    With a customization argument to make the vertical scale logarithmic:

      >>> da = pp.data.data1d()
      >>> in_node = pp.Node(da)
      >>> fig = pp.linefigure(in_node, norm='log')
    """

    return backends.figure2d(LineView, *args, **kwargs)
