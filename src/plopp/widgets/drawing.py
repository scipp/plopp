# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core import Node, node, View
from ..graphics import InteractiveFig1d, InteractiveFig2d
from .tools import ToggleTool
from functools import partial
import scipp as sc
from typing import Callable, Any, Union


def is_figure(x):
    return isinstance(x, (InteractiveFig1d, InteractiveFig2d))


class DrawingTool(ToggleTool):

    def __init__(self,
                 figure: View,
                 input_node: Node,
                 tool: Any,
                 func: Callable,
                 destination: Union[View, Node],
                 value: bool = False,
                 **kwargs):

        super().__init__(callback=self.start_stop, value=value, **kwargs)

        self._figure = figure
        self._input_node = input_node
        self._draw_nodes = {}
        self._output_nodes = {}
        self._func = func
        self._tool = tool(ax=self._figure.ax, autostart=False)
        self._destination = destination
        self._tool.on_create(self.make_node)
        self._tool.on_change(self.update_node)
        self._tool.on_remove(self.remove_node)

    def convert_raw_data(self, artist):
        return lambda: artist

    def make_node(self, artist):
        draw_node = Node(self.convert_raw_data(artist))
        nodeid = draw_node.id
        self._draw_nodes[nodeid] = draw_node
        artist.nodeid = nodeid
        output_node = node(self._func)(self._input_node, draw_node)
        self._output_nodes[nodeid] = output_node
        # print(self._destination, type(self._destination))
        if is_figure(self._destination):
            output_node.add_view(self._destination)
            self._destination.update(new_values=output_node(), key=output_node.id)
            self._destination.artists[output_node.id].color = artist.color
        elif isinstance(self._destination, Node):
            self._destination.parents.append(output_node)

    def update_node(self, artist):
        n = self._draw_nodes[artist.nodeid]
        n.func = self.convert_raw_data(artist)
        n.notify_children(artist)

    def remove_node(self, artist):
        nodeid = artist.nodeid
        draw_node = self._draw_nodes[nodeid]
        output_node = self._output_nodes[nodeid]
        if is_figure(self._destination):
            self._destination.artists[output_node.id].remove()
        output_node.remove()
        draw_node.remove()

    def start_stop(self):
        """
        Toggle start or stop of the tool.
        """
        if self.value:
            self._tool.start()
        else:
            self._tool.stop()


class PointsTool(DrawingTool):
    """
    Tool to add point markers onto a figure.

    Parameters
    ----------
    value:
        Set the toggle button value on creation.
    ax:
        The Matplotlib axes where the points will be drawn.
    """

    def __init__(self, value=False, **kwargs):
        from mpltoolbox import Points
        # Points(ax=ax, autostart=False, mec='w')
        super().__init__(value=value,
                         tool=partial(Points, mec='w'),
                         icon='crosshairs',
                         **kwargs)

    def convert_raw_data(self, artist):
        return lambda: {
            'x': {
                'dim': self._figure.dims['x'],
                'value': sc.scalar(artist.x, unit=self._figure.canvas.xunit)
            },
            'y': {
                'dim': self._figure.dims['y'],
                'value': sc.scalar(artist.y, unit=self._figure.canvas.yunit)
            },
        }
