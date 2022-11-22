# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core import Node, View, node
from ..graphics.fig2d import Figure2d
from .tools import DrawRectsTool
from .slice import slice_dims

from plopp import View
from typing import Dict, Any, Callable, Optional
import scipp as sc


def _get_patch_artist(change):
    """
    If the vertices of the rectangle are emitting events, we want to act on the
    rectangle patch.
    """
    return change['artist']._patch if hasattr(change['artist'],
                                              '_patch') else change['artist']


class ROITool(DrawRectsTool):
    """
    Tool to draw rectangular regions-of-interest on a 2D figure.
    An ``operation`` can be provided, which is a function that will be applied to the
    data selected inside the region-of-interest.

      - When a rectangle is added to the 2d figure, select new data and display it in
        the ``output_figure``.
      - When a rectangle is dragged or resized on the 2d figure, update the
        corresponding artist in the ``output_figure``.
      - When a rectangle is removed from the 2d figure, remove the corresponding artist
        from the ``output_figure``.

    Parameters
    ----------
    figure:
        The main (two_dimensional) figure where the tool will draw rectangles.
    output_figure:
        The secondary figure where the tool will display its results.
    operation:
        If provided, apply operation to the data selected in the ROI, before adding it
        to the ``output_figure``.
    """

    def __init__(self,
                 figure: View,
                 output_figure: View,
                 operation: Optional[Callable] = None):
        if len(figure.graph_nodes) > 1:
            raise ValueError("Cannot automatically generate tool because figure "
                             "has more than one artist.")
        self._root_node = list(figure.graph_nodes.values())[0]
        self._output_fig = output_figure
        self._operation = operation
        self._xdim = figure.dims['x']
        self._ydim = figure.dims['y']
        self._xunit = figure.canvas.xunit
        self._yunit = figure.canvas.yunit
        self._event_nodes = {}
        super().__init__(figure=figure)
        self.rects.on_create = self.make_node
        self.rects.on_vertex_release = self.update_node
        self.rects.on_drag_release = self.update_node
        self.rects.on_remove = self.remove_node

    def make_node(self, change: Dict[str, Any]):
        corners = change['artist'].get_corners()
        x = [c[0] for c in corners]
        y = [c[1] for c in corners]
        rect_node = Node(
            lambda: {
                self._xdim:
                slice(sc.scalar(min(x), unit=self._xunit),
                      sc.scalar(max(x), unit=self._xunit)),
                self._ydim:
                slice(sc.scalar(min(y), unit=self._yunit),
                      sc.scalar(max(y), unit=self._yunit))
            })
        self._event_nodes[rect_node.id] = rect_node
        change['artist'].nodeid = rect_node.id
        roi_node = slice_dims(self._root_node, rect_node)
        op_node = node(
            self._operation)(roi_node) if self._operation is not None else roi_node
        op_node.add_view(self._output_fig)
        self._output_fig.update(new_values=op_node.request_data(), key=op_node.id)
        self._output_fig.artists[op_node.id].color = change['artist'].get_edgecolor()

    def update_node(self, change):
        artist = _get_patch_artist(change)
        n = self._event_nodes[artist.nodeid]
        corners = artist.get_corners()
        x = [c[0] for c in corners]
        y = [c[1] for c in corners]
        n.func = lambda: {
            self._xdim:
            slice(sc.scalar(min(x), unit=self._xunit),
                  sc.scalar(max(x), unit=self._xunit)),
            self._ydim:
            slice(sc.scalar(min(y), unit=self._yunit),
                  sc.scalar(max(y), unit=self._yunit))
        }
        n.notify_children(change)

    def remove_node(self, change: Dict[str, Any]):
        n = self._event_nodes[_get_patch_artist(change).nodeid]
        pnode = n.children[0]
        self._output_fig.artists[pnode.id].remove()
        self._output_fig.canvas.draw()
        pnode.remove()
        n.remove()
