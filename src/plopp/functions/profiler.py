# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .common import require_interactive_backend, preprocess
from .figure import figure
from ..core import input_node, widget_node, Node
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
    sl = SliceWidget(da, dims=[dim])
    w = widget_node(sl)

    slice_node = slice_dims(a, w)
    f = figure(slice_node)

    prof = figure()

    def make_new_node(change):
        event = change['event']
        event_node = Node(
            func=lambda: {
                'xx': scalar(event.xdata, unit=da.meta['xx'].unit),
                'yy': scalar(event.ydata, unit=da.meta['yy'].unit)
            })
        profile_node = slice_dims(a, event_node)
        prof._graph_nodes[str(uuid.uuid1())] = profile_node
        profile_node.add_view(prof)
        prof.render()

    f.toolbar['profile'] = PointsTool(ax=f._ax)
    f.toolbar['profile'].points.on_create = make_new_node
    return Box([sl, f, prof])
