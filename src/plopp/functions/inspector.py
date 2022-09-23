# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .common import require_interactive_backend, preprocess
from .figure import figure
from ..core import input_node, widget_node, Node
from ..core.utils import coord_as_bin_edges
from ..widgets import PointsTool

from scipp import Variable, scalar
from scipp.typing import VariableLike
from numpy import ndarray
from typing import Union, Dict, List


def inspector(obj: Union[VariableLike, ndarray],
              keep: List[str] = None,
              *,
              crop: Dict[str, Dict[str, Variable]] = None,
              **kwargs):
    """
    Plot a three-dimensional object by slicing one of the dimensions.
    This will produce a two-dimensional image figure, with a slider below.
    In addition, a 'inspection' tool is available in the toolbar which allows to place
    markers on the image which perform slicing at that position along the third
    dimension and displays the resulting one-dimensional slice on the right hand side
    figure.

    Controls:
    - Left-click to make new point
    - Left-click and hold on point to move point
    - Middle-click to delete point

    Parameters
    ----------
    obj:
        The object to be plotted.
    keep:
        The dimensions to be kept, all remaining dimensions will be sliced. This should
        be a list of dims. If no dims are provided, the last dim will be kept in the
        case of a 2-dimensional input, while the last two dims will be kept in the case
        of higher dimensional inputs.
    crop:
        Set the axis limits. Limits should be given as a dict with one entry per
        dimension to be cropped. Each entry should be a nested dict containing scalar
        values for `'min'` and/or `'max'`. Example:
        `da.plot(crop={'time': {'min': 2 * sc.Unit('s'), 'max': 40 * sc.Unit('s')}})`
    **kwargs:
        See :py:func:`plopp.plot` for the full list of figure customization arguments.

    Returns
    -------
    :
        A :class:`Box` which will contain two :class:`Figure` and one slider widget.
    """
    require_interactive_backend('inspector')

    from plopp.widgets import SliceWidget, slice_dims, Box
    da = preprocess(obj, crop=crop, ignore_size=True)

    a = input_node(da)

    if keep is None:
        keep = da.dims[-(2 if da.ndim > 2 else 1):]

    # Convert dimension coords to bin edges
    for d in keep:
        da.coords[d] = coord_as_bin_edges(da, d)

    sl = SliceWidget(da, dims=list(set(da.dims) - set(keep)))
    w = widget_node(sl)

    slice_node = slice_dims(a, w)
    f2d = figure(slice_node, **{**{'crop': crop}, **kwargs})
    xdim = f2d._dims['x']['dim']
    ydim = f2d._dims['y']['dim']

    f1d = figure()

    event_nodes = {}

    def make_node(change):
        event = change['event']
        event_node = Node(
            func=lambda: {
                xdim: scalar(event.xdata, unit=da.meta[xdim].unit),
                ydim: scalar(event.ydata, unit=da.meta[ydim].unit)
            })
        event_nodes[event_node.id] = event_node
        change['artist'].nodeid = event_node.id
        inspect_node = slice_dims(a, event_node)
        f1d.graph_nodes[inspect_node.id] = inspect_node
        inspect_node.add_view(f1d)
        f1d.render()

    def update_node(change):
        event = change['event']
        n = event_nodes[change['artist'].nodeid]
        n.func = lambda: {
            xdim: scalar(event.xdata, unit=da.meta[xdim].unit),
            ydim: scalar(event.ydata, unit=da.meta[ydim].unit)
        }
        n.notify_children(change)

    def remove_node(change):
        n = event_nodes[change['artist'].nodeid]
        pnode = n.children[0]
        f1d._children[pnode.id].remove()
        f1d.draw()
        pnode.remove()
        n.remove()

    pts = PointsTool(ax=f2d._ax, tooltip='Add inspector points')
    pts.points.on_create = make_node
    pts.points.on_vertex_move = update_node
    pts.points.on_remove = remove_node
    f2d.toolbar['inspect'] = pts
    return Box([[f2d, f1d], sl])
