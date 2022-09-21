# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .common import require_interactive_backend, preprocess
from .figure import figure
from ..core import input_node, widget_node

from scipp import Variable
from scipp.typing import VariableLike
from numpy import ndarray
from typing import Union, Dict, List


def profiler(obj: Union[VariableLike, ndarray],
             dim: str = None,
             *,
             crop: Dict[str, Dict[str, Variable]] = None,
             **kwargs):
    """
    """
    require_interactive_backend('profiler')

    from plopp.widgets import SliceWidget, slice_dims, Box
    da = preprocess(obj, crop=crop, ignore_size=True)

    a = pp.input_node(da)

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 1, figsize=(6, 8))

    if dim is None:
        dim = da.dims[-1]
    sl = SliceWidget(da, dims=[dim])
    w = pp.widget_node(sl)

    slice_node = slice_dims(a, w)
    f = pp.figure(slice_node, ax=ax[0])

    points = tbx.Points(ax=ax[0])

    prof = pp.figure(ax=ax[1])

    # event_node = pp.Node(func=lambda: {d: 0 for d in (set(da.dims) - set([dim]))})
    def make_new_node(change):
        event = change['event']
        event_node = pp.Node(
            func=lambda: {
                'xx': sc.scalar(event.xdata, unit=da.meta['xx'].unit),
                'yy': sc.scalar(event.ydata, unit=da.meta['xx'].unit)
            })
        profile_node = slice_dims(a, event_node)
        # id =
        prof._graph_nodes[str(uuid.uuid1())] = profile_node
        profile_node.add_view(prof)
        prof.render()

    # event_node = pp.Node(func=lambda: {d: 0 for d in (set(da.dims) - set([dim]))})

    # def handle_event(change):
    #     event = change['event']
    #     print(event)
    #     if None not in (event.xdata, event.ydata):
    #         event_node.func = lambda: {'xx': sc.scalar(event.xdata, unit=da.meta['xx'].unit),
    #                                    'yy': sc.scalar(event.ydata, unit=da.meta['xx'].unit)}
    #         event_node.notify_children(event)

    points.on_create = make_new_node

    return Box([sl, f])

    # a = input_node(da)

    # if dim is None:
    #     dim = da.dims[-1]
    # sl = SliceWidget(da, dims=[dim])
    # w = widget_node(sl)
    # slice_node = slice_dims(a, w)
    # fig = figure(slice_node, **{**{'crop': crop}, **kwargs})
    # return Box([fig, sl])
