# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from functools import partial
from typing import Literal

import numpy as np
import scipp as sc
from matplotlib.path import Path

from ..core import Node
from ..core.typing import Plottable
from ..core.utils import coord_as_bin_edges
from ..graphics import imagefigure, linefigure
from .common import preprocess, require_interactive_figure


def _to_bin_edges(da: sc.DataArray, dim: str) -> sc.DataArray:
    """
    Convert dimension coords to bin edges.
    """
    print(dim)
    for d in set(da.dims) - set(dim):
        da.coords[d] = coord_as_bin_edges(da, d)
    return da


def _to_bin_centers(da: sc.DataArray, dim: str) -> sc.DataArray:
    """
    Convert dimension coords to bin centers.
    """
    for d in set(da.dims) - set(dim):
        da.coords[d] = sc.midpoints(da.coords[d], dim=d)
    return da


def _apply_op(da: sc.DataArray, op: str, dim: str) -> sc.DataArray:
    out = getattr(sc, op)(da, dim=dim)
    if out.name:
        out.name = f'{op} of {out.name}'
    return out


def _slice_xy(da: sc.DataArray, xy: dict[str, dict[str, int]]) -> sc.DataArray:
    x = xy['x']
    y = xy['y']
    try:
        # If there is a 2D coordinate in the data, we need to slice the other dimension
        # first, as trying to slice a 2D coordinate using label-based indexing raises an
        # error in Scipp. After slicing the other dimension, the 2D coordinate will be
        # 1D and can be sliced normally using label-based indexing.
        # We assume here that there would only be one multi-dimensional coordinate in a
        # given DataArray (which is very likely the case).
        if da.coords[y['dim']].ndim > 1:
            return da[x['dim'], x['value']][y['dim'], y['value']]
        else:
            return da[y['dim'], y['value']][x['dim'], x['value']]
    except IndexError:
        # If the index is out of bounds, return an empty DataArray
        return sc.full_like(da[y['dim'], 0][x['dim'], 0], value=np.nan, dtype=float)


def _mask_outside_polygon(
    da: sc.DataArray,
    poly: dict,
    points: np.ndarray,
    sizes: dict[str, int],
    op: str,
    non_nan: sc.Variable,
) -> sc.DataArray:
    vx = poly['x']['value'].values
    vy = poly['y']['value'].values
    verts = np.column_stack([vx, vy])
    path = Path(verts)
    dims = sizes.keys()
    inside = sc.array(
        dims=dims,
        values=path.contains_points(points).reshape(tuple(sizes.values())),
    )
    masked = da.assign_masks({str(da.masks.keys()): ~inside})
    # If the operation is a mean, there is currently a bug in the implementation
    # in scipp where doing a mean over a subset of the array's dimensions gives the
    # wrong result: https://github.com/scipp/scipp/issues/3841
    # Instead, we manually compute the mean
    if 'mean' not in op:
        return getattr(masked, op)(dims)
    if 'nan' in op:
        numerator = masked.nansum(dims)
        denominator = (inside & non_nan).sum()
    else:
        numerator = masked.sum(dims)
        denominator = inside.sum()
    denominator.unit = ""
    return numerator / denominator


def inspector(
    obj: Plottable,
    dim: str | None = None,
    *,
    aspect: Literal['auto', 'equal'] | None = None,
    autoscale: bool = True,
    cbar: bool = True,
    clabel: str | None = None,
    cmax: sc.Variable | float | None = None,
    cmin: sc.Variable | float | None = None,
    errorbars: bool = True,
    figsize: tuple[float, float] | None = None,
    grid: bool = False,
    legend: bool | tuple[float, float] = True,
    logc: bool | None = None,
    mask_cmap: str = 'gray',
    mask_color: str = 'black',
    mode: Literal['point', 'polygon', 'rectangle'] = 'point',
    nan_color: str | None = None,
    norm: Literal['linear', 'log'] | None = None,
    operation: Literal[
        'sum', 'mean', 'min', 'max', 'nansum', 'nanmean', 'nanmin', 'nanmax'
    ] = 'sum',
    orientation: Literal['horizontal', 'vertical'] = 'horizontal',
    title: str | None = None,
    vmax: sc.Variable | float | None = None,
    vmin: sc.Variable | float | None = None,
    xlabel: str | None = None,
    xmax: sc.Variable | float | None = None,
    xmin: sc.Variable | float | None = None,
    ylabel: str | None = None,
    ymax: sc.Variable | float | None = None,
    ymin: sc.Variable | float | None = None,
    **kwargs,
):
    """
    Inspector takes in a three-dimensional input and applies a reduction operation
    (``'sum'`` by default) along one of the dimensions specified by ``dim``.
    It displays the result as a two-dimensional image.
    In addition, an 'inspection' tool is available in the toolbar. In ``mode='point'``
    it allows placing point markers on the image to slice at that position, retaining
    only the third dimension and displaying the resulting one-dimensional slice in the
    right-hand side figure. In ``mode='polygon'`` it allows drawing a polygon to compute
    the total intensity inside the polygon as a function of the third dimension.
    In ``mode='rectangle'`` it allows drawing a rectangle to compute the total intensity
    inside the rectangle as a function of the third dimension.

    Controls (point mode):
    - Left-click to make new points
    - Left-click and hold on point to move point
    - Middle-click to delete point

    Controls (rectangle mode):
    - Left-click to make new rectangles
    - Left-click and hold on rectangle vertices to resize rectangle
    - Right-click and hold to drag/move the entire rectangle
    - Middle-click to delete rectangle

    Controls (polygon mode):
    - Left-click to make new polygons
    - Left-click and hold on polygon vertex to move vertex
    - Right-click and hold to drag/move the entire polygon
    - Middle-click to delete polygon

    Notes
    -----

    Almost all the arguments for plot customization apply to the two-dimensional image
    (unless specified).

    Parameters
    ----------
    obj:
        The object to be plotted.
    dim:
        The dimension along which to apply the reduction operation. This will also be
        the dimension that remains in the one-dimensional slices generated by adding
        markers on the image. If no dim is provided, the last (inner) dim of the input
        data will be used.
    aspect:
        Aspect ratio for the axes.
    autoscale:
        Automatically scale the axes/colormap on updates if ``True``.
    cbar:
        Show colorbar if ``True``.
    clabel:
        Label for colorscale.
    cmax:
        Upper limit for colorscale.
    cmin:
        Lower limit for colorscale.
    errorbars:
        Show errorbars if ``True`` (1d figure).
    figsize:
        The width and height of the figure, in inches.
    grid:
        Show grid if ``True``.
    legend:
        Show legend if ``True``. If ``legend`` is a tuple, it should contain the
        ``(x, y)`` coordinates of the legend's anchor point in axes coordinates
        (1d figure).
    logc:
        If ``True``, use logarithmic scale for colorscale.
    mask_cmap:
        Colormap to use for masks.
    mask_color:
        Color of masks (overrides ``mask_cmap``).
    mode:
        Select ``'point'`` for point inspection, ``'polygon'`` for polygon selection,
        or ``'rectangle'`` for rectangle selection with total intensity inside the
        shape plotted as a function of ``dim``.
    nan_color:
        Color to use for NaN values.
    norm:
        Set to ``'log'`` for a logarithmic colorscale. Legacy, prefer ``logc`` instead.
    operation:
        The operation to apply along the third (undisplayed) dimension specified by
        ``dim``. The same operation is also applied to the data within the selected
        region in the case of ``polygon`` and ``rectangle`` modes.
    orientation:
        Display the two panels side-by-side ('horizontal') or one below the other
        ('vertical').
    title:
        The figure title.
    vmax:
        Upper limit for data colorscale to be displayed.
        Legacy, prefer ``cmax`` instead.
    vmin:
        Lower limit for data colorscale to be displayed.
        Legacy, prefer ``cmin`` instead.
    xlabel:
        Label for x-axis.
    xmax:
        Upper limit for x-axis (1d figure)
    xmin:
        Lower limit for x-axis (1d figure)
    ylabel:
        Label for y-axis.
    ymax:
        Upper limit for y-axis (1d figure).
    ymin:
        Lower limit for y-axis (1d figure).
    **kwargs:
        Additional arguments forwarded to the underlying plotting library.

    Returns
    -------
    :
        A :class:`Box` which will contain two :class:`Figure` and one slider widget.
    """

    if mode not in ['point', 'polygon', 'rectangle']:
        raise ValueError(
            f'Invalid mode: {mode}. Allowed modes are "point", "polygon", "rectangle".'
        )

    in_node = Node(preprocess, obj, ignore_size=True)
    data = in_node()
    data_dims = data.dims

    if dim is None:
        dim = data_dims[-(len(data_dims) - 2) :]
    if isinstance(dim, str):
        dim = [dim]

    dummy = data
    for d in set(data_dims) - set(dim):
        dummy = dummy[d, 0]
    dummy = dummy.copy()
    dummy.data = sc.full_like(dummy.data, value=np.nan, dtype=float)

    if len(data_dims) == 3:
        secondary_fig = linefigure(
            Node(dummy),
            autoscale=autoscale,
            errorbars=errorbars,
            grid=grid,
            legend=legend,
            mask_color=mask_color,
            xmax=xmax,
            xmin=xmin,
            ymax=ymax,
            ymin=ymin,
        )
    elif len(data_dims) == 4:
        secondary_fig = imagefigure(
            Node(dummy),
            aspect=aspect,
            autoscale=autoscale,
            cbar=cbar,
            clabel=clabel,
            cmax=cmax,
            cmin=cmin,
            # errorbars=errorbars,
            # figsize=figsize,
            grid=grid,
            logc=logc,
            mask_cmap=mask_cmap,
            mask_color=mask_color,
            nan_color=nan_color,
            norm=norm,
            # title=title,
            vmax=vmax,
            vmin=vmin,
            # xlabel=xlabel,
            # ylabel=ylabel,
        )
    require_interactive_figure(secondary_fig, 'inspector')

    # in_node = Node(preprocess, obj, ignore_size=True)
    # data = in_node()
    # if data.ndim != 3:
    #     raise ValueError(
    #         'The inspector plot currently only works with '
    #         f'three-dimensional data, found {data.ndim} dims.'
    #     )
    if dim is None:
        dim = data_dims[-(len(data_dims) - 2) :]
    if isinstance(dim, str):
        dim = [dim]
    bin_edges_node = Node(_to_bin_edges, in_node, dim=dim)
    bin_centers_node = Node(_to_bin_centers, bin_edges_node, dim=dim)
    op_node = Node(_apply_op, da=bin_edges_node, op=operation, dim=dim)
    main_fig = imagefigure(
        op_node,
        aspect=aspect,
        cbar=cbar,
        clabel=clabel,
        cmax=cmax,
        cmin=cmin,
        figsize=figsize,
        grid=grid,
        logc=logc,
        mask_cmap=mask_cmap,
        mask_color=mask_color,
        nan_color=nan_color,
        norm=norm,
        title=title,
        vmax=vmax,
        vmin=vmin,
        xlabel=xlabel,
        ylabel=ylabel,
        **kwargs,
    )
    from ..widgets import Box, PointsTool, PolygonTool, RectangleTool

    if mode == 'point':
        tool = PointsTool(
            figure=main_fig,
            input_node=bin_edges_node,
            func=_slice_xy,
            destination=secondary_fig,
            tooltip="Activate inspector tool",
        )
    else:
        da = bin_centers_node()
        xdim = main_fig.canvas.dims['x']
        ydim = main_fig.canvas.dims['y']
        x = da.coords[xdim]
        y = da.coords[ydim]
        sizes = {**x.sizes, **y.sizes}
        xx = sc.broadcast(x, sizes=sizes)
        yy = sc.broadcast(y, sizes=sizes)
        points = np.column_stack([xx.values.ravel(), yy.values.ravel()])
        non_nan = ~sc.isnan(da.data)
        tools = {'polygon': PolygonTool, 'rectangle': RectangleTool}
        tool = tools[mode](
            figure=main_fig,
            input_node=bin_centers_node,
            func=partial(
                _mask_outside_polygon,
                points=points,
                sizes=sizes,
                op=operation,
                non_nan=non_nan,
            ),
            destination=secondary_fig,
            tooltip=f"Activate {mode} inspector tool",
        )

    main_fig.toolbar['inspect'] = tool
    out = [main_fig, secondary_fig]
    if orientation == 'horizontal':
        out = [out]
    return Box(out)
