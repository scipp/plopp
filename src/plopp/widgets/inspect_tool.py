# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core import Node, View
from ..graphics.fig2d import Figure2d
from .tools import DrawPointsTool

import scipp as sc
from typing import Any, Dict


class InspectTool(DrawPointsTool):
    """
    Tool to inspect the third (not displayed/into-the-paper) dimension of a 3d data
    array.

      - When a point is added to the 2d figure, make a new line in the 1d figure.
      - When a point is dragged on the 2d figure, update the corresponding line in the
        1d figure.
      - When a point is removed from the 2d figure, remove the corresponding line from
        the 1d figure.
    """

    def __init__(self, figure: View, root_node: Node, fig1d: View):
        if not isinstance(figure, Figure2d):
            raise TypeError("The inspect tool is only designed to work on 2d figures.")
        self._root_node = root_node
        self._data_array = self._root_node.request_data()
        self._fig1d = fig1d
        self._event_nodes = {}
        self._xdim = figure.dims['x']
        self._ydim = figure.dims['y']
        super().__init__(figure=figure)
        self.points.on_create = self.make_node
        self.points.on_vertex_move = self.update_node
        self.points.on_remove = self.remove_node

    def make_node(self, change: Dict[str, Any]):
        from ..widgets import slice_dims
        event = change['event']
        event_node = Node(
            func=lambda: {
                self._xdim:
                sc.scalar(event.xdata, unit=self._data_array.meta[self._xdim].unit),
                self._ydim:
                sc.scalar(event.ydata, unit=self._data_array.meta[self._ydim].unit)
            })
        self._event_nodes[event_node.id] = event_node
        change['artist'].nodeid = event_node.id
        inspect_node = slice_dims(self._root_node, event_node)
        inspect_node.add_view(self._fig1d)
        self._fig1d.update(new_values=inspect_node.request_data(), key=inspect_node.id)
        self._fig1d.artists[inspect_node.id].color = change['artist'].get_color()

    def update_node(self, change: Dict[str, Any]):
        event = change['event']
        n = self._event_nodes[change['artist'].nodeid]
        n.func = lambda: {
            self._xdim: sc.scalar(event.xdata,
                                  unit=self._data_array.meta[self._xdim].unit),
            self._ydim: sc.scalar(event.ydata,
                                  unit=self._data_array.meta[self._ydim].unit)
        }
        n.notify_children(change)

    def remove_node(self, change: Dict[str, Any]):
        n = self._event_nodes[change['artist'].nodeid]
        pnode = n.children[0]
        self._fig1d.artists[pnode.id].remove()
        self._fig1d.canvas.draw()
        pnode.remove()
        n.remove()
