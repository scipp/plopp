# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core.utils import name_with_unit
from .basefig import BaseFig
from .canvas import Canvas
from .colormapper import ColorMapper
from .mesh import Mesh

import scipp as sc
from typing import Any, Dict, Literal, Optional, Tuple, Union


class Figure2d(BaseFig):
    """
    Figure that makes a visual representation of two-dimensional data.
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
    scale:
        Control the scaling of the horizontal axis.
    aspect:
        Aspect ratio for the axes.
    grid:
        Show grid if ``True``.
    crop:
        Set the axis limits. Limits should be given as a dict with one entry per
        dimension to be cropped.
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
        All other kwargs are forwarded to the Mesh artist.
    """

    def __init__(self,
                 *nodes,
                 cmap: str = 'viridis',
                 mask_cmap: str = 'gray',
                 norm: Literal['linear', 'log'] = 'linear',
                 vmin: Optional[Union[sc.Variable, int, float]] = None,
                 vmax: Optional[Union[sc.Variable, int, float]] = None,
                 scale: Optional[Dict[str, str]] = None,
                 aspect: Literal['auto', 'equal'] = 'auto',
                 grid: bool = False,
                 crop: Optional[Dict[str, Dict[str, sc.Variable]]] = None,
                 cbar: bool = True,
                 title: Optional[str] = None,
                 figsize: Tuple[float, float] = (6., 4.),
                 ax: Optional[Any] = None,
                 cax: Optional[Any] = None,
                 format: Optional[Literal['svg', 'png']] = None,
                 **kwargs):

        super().__init__(*nodes)

        self._scale = {} if scale is None else scale
        self._kwargs = kwargs
        self._repr_format = format
        self.canvas = Canvas(cbar=cbar,
                             aspect=aspect,
                             grid=grid,
                             title=title,
                             figsize=figsize,
                             ax=ax,
                             cax=cax)
        self.colormapper = ColorMapper(cmap=cmap,
                                       mask_cmap=mask_cmap,
                                       norm=norm,
                                       vmin=vmin,
                                       vmax=vmax,
                                       cax=self.canvas.cax)

        self.render()
        self.canvas.autoscale()
        if crop is not None:
            self.crop(**crop)
        self.canvas.fit_to_page()

    def update(self, new_values: sc.DataArray, key: str, draw: bool = True):
        """
        Add new image or update image array with new values.

        Parameters
        ----------
        new_values:
            New data to create or update a :class:`Mesh` object from.
        key:
            The id of the node that sent the new data.
        draw:
            Draw the figure after the update if ``True``. Set this to ``False`` when
            doing batch updates of multiple artists, and then manually call ``draw``
            once all artists have been updated.
        """
        if new_values.ndim != 2:
            raise ValueError("Figure2d can only be used to plot 2-D data.")

        self.colormapper.update(data=new_values, key=key)

        if key not in self.artists:

            mesh = Mesh(canvas=self.canvas, data=new_values, **self._kwargs)
            self.artists[key] = mesh
            self.colormapper[key] = mesh
            self.dims.update({"x": new_values.dims[1], "y": new_values.dims[0]})

            self.canvas.xunit = new_values.meta[new_values.dims[1]].unit
            self.canvas.yunit = new_values.meta[new_values.dims[0]].unit
            self.canvas.xlabel = name_with_unit(var=new_values.meta[self.dims['x']])
            self.canvas.ylabel = name_with_unit(var=new_values.meta[self.dims['y']])
            if self.dims['x'] in self._scale:
                self.canvas.xscale = self._scale[self.dims['x']]
            if self.dims['y'] in self._scale:
                self.canvas.yscale = self._scale[self.dims['y']]

        self.artists[key].update(new_values=new_values)
        self.artists[key].set_colors(self.colormapper.rgba(self.artists[key].data))

        if draw:
            self.canvas.draw()

    def toggle_norm(self):
        """
        Toggle the colormapper norm.
        """
        self.colormapper.toggle_norm()
        self.canvas.draw()

    def crop(self, **limits):
        """
        Set the axes limits according to the crop parameters.

        Parameters
        ----------
        **limits:
            Min and max limits for each dimension to be cropped.
        """
        self.canvas.crop(**{xy: limits[self.dims[xy]] for xy in 'xy'})
