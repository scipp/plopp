# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core.utils import name_with_unit
from .basefig import BaseFig
from .canvas import Canvas
from .line import Line

import scipp as sc
from typing import Any, Dict, Literal, Optional, Tuple, Union


class Figure1d(BaseFig):
    """
    Figure that makes a visual representation of one-dimensional data.
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
    scale:
        Control the scaling of the horizontal axis.
    errorbars:
        Hide errorbars if ``False``.
    mask_color:
        The color of the masks.
    aspect:
        Aspect ratio for the axes.
    grid:
        Show grid if ``True``.
    crop:
        Set the axis limits. Limits should be given as a dict with one entry per
        dimension to be cropped.
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
    **kwargs:
        All other kwargs are forwarded to Matplotlib:

        - ``matplotlib.pyplot.plot`` for 1d data with a non bin-edge coordinate
        - ``matplotlib.pyplot.step`` for 1d data with a bin-edge coordinate
    """

    def __init__(self,
                 *nodes,
                 norm: Literal['linear', 'log'] = 'linear',
                 vmin: Optional[Union[sc.Variable, int, float]] = None,
                 vmax: Optional[Union[sc.Variable, int, float]] = None,
                 scale: Optional[Dict[str, str]] = None,
                 errorbars: bool = True,
                 mask_color: str = 'black',
                 aspect: Literal['auto', 'equal'] = 'auto',
                 grid: bool = False,
                 crop: Optional[Dict[str, Dict[str, sc.Variable]]] = None,
                 title: Optional[str] = None,
                 figsize: Tuple[float, float] = (6., 4.),
                 ax: Optional[Any] = None,
                 format: Optional[Literal['svg', 'png']] = None,
                 **kwargs):

        super().__init__(*nodes)

        self._scale = {} if scale is None else scale
        self._errorbars = errorbars
        self._mask_color = mask_color
        self._kwargs = kwargs
        self._repr_format = format
        self.canvas = Canvas(cbar=False,
                             aspect=aspect,
                             grid=grid,
                             figsize=figsize,
                             title=title,
                             ax=ax,
                             vmin=vmin,
                             vmax=vmax)
        self.canvas.yscale = norm

        self.render()
        self.canvas.autoscale()
        if crop is not None:
            self.crop(**crop)
        self.canvas.fit_to_page()

    def update(self, new_values: sc.DataArray, key: str, draw: bool = True):
        """
        Add new line or update line values.

        Parameters
        ----------
        new_values:
            New data to create or update a :class:`Line` object from.
        key:
            The id of the node that sent the new data.
        draw:
            Draw the figure after the update if ``True``. Set this to ``False`` when
            doing batch updates of multiple artists, and then manually call ``draw``
            once all artists have been updated.
        """
        if new_values.ndim != 1:
            raise ValueError("Figure1d can only be used to plot 1-D data.")

        if key not in self.artists:

            line = Line(canvas=self.canvas,
                        data=new_values,
                        number=len(self.artists),
                        errorbars=self._errorbars,
                        mask_color=self._mask_color,
                        **self._kwargs)
            self.artists[key] = line
            if line.label:
                self.canvas.legend()
            self.dims['x'] = new_values.dim

            self.canvas.xunit = new_values.meta[new_values.dim].unit
            self.canvas.yunit = new_values.unit
            self.canvas.xlabel = name_with_unit(var=new_values.meta[self.dims['x']])
            self.canvas.ylabel = name_with_unit(var=new_values.data, name="")

            if self.dims['x'] in self._scale:
                self.canvas.xscale = self._scale[self.dims['x']]

        else:
            self.artists[key].update(new_values=new_values)

        if draw:
            self.canvas.autoscale()

    def crop(self, **limits):
        """
        Set the axes limits according to the crop parameters.

        Parameters
        ----------
        **limits:
            Min and max limits for each dimension to be cropped.
        """
        self.canvas.crop(x=limits[self.dims['x']])
