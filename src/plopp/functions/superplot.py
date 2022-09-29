# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .common import require_interactive_backend, preprocess
from .figure import figure
from ..core import input_node, node, Node, widget_node
from ..core.utils import coord_as_bin_edges
from ..widgets import PointsTool, ColorTool

import scipp as sc
from numpy import ndarray
from typing import Union, Dict, Literal
from matplotlib.colors import to_hex


class LineSaveTool:

    def __init__(self, data_node, slider_node, fig):
        import ipywidgets as ipw
        self._data_node = data_node
        self._slider_node = slider_node
        self._fig = fig
        self._copy_nodes = {}
        self.button = ipw.Button(description='Save line')
        self.button.on_click(self.save_line)
        self.container = ipw.VBox()
        self.widget = ipw.VBox([self.button, self.container])

    def save_line(self, change):
        from plopp.widgets import slice_dims
        line_node = input_node(self._data_node.request_data())
        self._copy_nodes[line_node.id] = line_node
        self._fig.graph_nodes[line_node.id] = line_node
        line_node.add_view(self._fig)
        self._fig.render()
        self.container.children = self.container.children + (ColorTool(
            text='line1', color=to_hex(self._fig._children[line_node.id].color)), )

    # def update_node(self, change):
    #     event = change['event']
    #     n = self._event_nodes[change['artist'].nodeid]
    #     n.func = lambda: {
    #         self._xdim: sc.scalar(event.xdata,
    #                               unit=self._data_array.meta[self._xdim].unit),
    #         self._ydim: sc.scalar(event.ydata,
    #                               unit=self._data_array.meta[self._ydim].unit)
    #     }
    #     n.notify_children(change)

    # def remove_node(self, change):
    #     n = self._event_nodes[change['artist'].nodeid]
    #     pnode = n.children[0]
    #     self._fig1d._children[pnode.id].remove()
    #     self._fig1d.draw()
    #     pnode.remove()
    #     n.remove()


def superplot(obj: Union[sc.typing.VariableLike, ndarray],
              keep: str = None,
              *,
              operation: Literal['sum', 'mean', 'min', 'max'] = 'sum',
              crop: Dict[str, Dict[str, sc.Variable]] = None,
              **kwargs):
    """
    """
    require_interactive_backend('slicer')

    from plopp.widgets import SliceWidget, slice_dims, Box
    da = preprocess(obj, crop=crop, ignore_size=True)
    a = input_node(da)

    if keep is None:
        keep = da.dims[-1]
    sl = SliceWidget(da, dims=list(set(da.dims) - set([keep])))
    w = widget_node(sl)
    slice_node = slice_dims(a, w)
    fig = figure(slice_node, **{**{'crop': crop}, **kwargs})
    save_tool = LineSaveTool(data_node=slice_node, slider_node=w, fig=fig)
    return Box([[fig, save_tool.widget], sl])
