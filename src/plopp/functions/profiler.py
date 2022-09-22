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


def profiler(obj: Union[VariableLike, ndarray],
             dim: str = None,
             *,
             crop: Dict[str, Dict[str, Variable]] = None,
             **kwargs):
    """
    """
    require_interactive_backend('profiler')

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
    f = figure(slice_node)

    prof = figure()

    event_nodes = {}

    def make_node(change):
        event = change['event']
        event_node = Node(
            func=lambda: {
                'xx': scalar(event.xdata, unit=da.meta['xx'].unit),
                'yy': scalar(event.ydata, unit=da.meta['yy'].unit)
            })
        event_nodes[event_node.id] = event_node
        change['artist'].nodeid = event_node.id
        profile_node = slice_dims(a, event_node)
        prof.graph_nodes[profile_node.id] = profile_node
        profile_node.add_view(prof)
        prof.render()

    def update_node(change):
        event = change['event']
        n = event_nodes[change['artist'].nodeid]
        n.func = lambda: {
            'xx': scalar(event.xdata, unit=da.meta['xx'].unit),
            'yy': scalar(event.ydata, unit=da.meta['yy'].unit)
        }
        n.notify_children(change)

    def remove_node(change):
        artist = change['artist']
        n = event_nodes[change['artist'].nodeid]
        pnode = n.children[0]
        prof._children[pnode.id].remove()
        prof.draw()
        pnode.remove()
        n.remove()

    pts = PointsTool(ax=f._ax)
    pts.points.on_create = make_node
    pts.points.on_vertex_move = update_node
    pts.points.on_remove = remove_node
    f.toolbar['profile'] = pts
    return Box([sl, f, prof])
