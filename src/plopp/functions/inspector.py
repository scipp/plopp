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
import uuid


def inspector(obj: Union[VariableLike, ndarray],
              dim: str = None,
              *,
              crop: Dict[str, Dict[str, Variable]] = None,
              **kwargs):
    """
    """
    require_interactive_backend('inspector')

    from plopp.widgets import SliceWidget, slice_dims, Box
    from mpltoolbox import Points
    da = preprocess(obj, crop=crop, ignore_size=True)

    a = input_node(da)

    if dim is None:
        dim = da.dims[-1]

    # Convert dimension coords to bin edges
    for d in (set(da.dims) - set([dim])):
        da.coords[d] = coord_as_bin_edges(da, d)

    sl = SliceWidget(da, dims=[dim])
    w = widget_node(sl)

    slice_node = slice_dims(a, w)
    f2d = figure(slice_node)
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
        artist = change['artist']
        n = event_nodes[change['artist'].nodeid]
        pnode = n.children[0]
        f1d._children[pnode.id].remove()
        f1d.draw()
        pnode.remove()
        n.remove()

    pts = PointsTool(ax=f2d._ax)
    pts.points.on_create = make_node
    pts.points.on_vertex_move = update_node
    pts.points.on_remove = remove_node
    f2d.toolbar['inspect'] = pts
    return Box([sl, f2d, f1d])
