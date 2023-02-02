# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from functools import partial
from typing import Any, Callable, Union

import scipp as sc

from ..core import Node, View, node
from .tools import ToggleTool


def is_figure(x):
    from ..backends.matplotlib.interactive import InteractiveFig
    return isinstance(x, InteractiveFig)


class DrawingTool(ToggleTool):
    """
    Interface between Plopp and Mpltoolbox.

    Parameters
    ----------
    figure:
        The figure where the tool will draw things (points, lines, shapes...).
    input_node:
        The node that provides the raw data which is shown in ``figure``.
    tool:
        The Mpltoolbox tool to use (Points, Lines, Rectangles, Ellipses...).
    func:
        The function to be used to make a node whose parents will be the ``input_node``
        and a node yielding the current state of the tool (current position, size).
    destination:
        Where the output from the ``func`` node will be then sent on. This can either
        be a figure, or another graph node.
    get_artist_info:
        A function that returns another function which will convert the properties of
        the artist that produced the event to something (usually a dict) that is usable
        by the ``destination``.
    value:
        Activate the tool upon creation if ``True``.
    **kwargs:
        Additional arguments are forwarded to the ``ToggleTool`` constructor.
    """

    def __init__(self,
                 figure: View,
                 input_node: Node,
                 tool: Any,
                 func: Callable,
                 destination: Union[View, Node],
                 get_artist_info: Callable,
                 value: bool = False,
                 **kwargs):

        super().__init__(callback=self.start_stop, value=value, **kwargs)

        self._figure = figure
        self._destination_is_fig = is_figure(self._figure)
        self._input_node = input_node
        self._draw_nodes = {}
        self._output_nodes = {}
        self._func = func
        self._tool = tool(ax=self._figure.ax, autostart=False)
        self._destination = destination
        self._get_artist_info = get_artist_info
        self._tool.on_create(self.make_node)
        self._tool.on_change(self.update_node)
        self._tool.on_remove(self.remove_node)

    def make_node(self, artist):
        draw_node = Node(self._get_artist_info(artist=artist, figure=self._figure))
        draw_node.name = f'Draw node {len(self._draw_nodes)}'
        nodeid = draw_node.id
        self._draw_nodes[nodeid] = draw_node
        artist.nodeid = nodeid
        output_node = node(self._func)(self._input_node, draw_node)
        output_node.name = f'Output node {len(self._output_nodes)}'
        self._output_nodes[nodeid] = output_node
        if self._destination_is_fig:
            output_node.add_view(self._destination._fig)
            self._destination.update(new_values=output_node(), key=output_node.id)
            self._destination.artists[output_node.id].color = artist.color if hasattr(
                artist, 'color') else artist.edgecolor
        elif isinstance(self._destination, Node):
            self._destination.parents.append(output_node)

    def update_node(self, artist):
        n = self._draw_nodes[artist.nodeid]
        n.func = self._get_artist_info(artist=artist, figure=self._figure)
        n.notify_children(artist)

    def remove_node(self, artist):
        nodeid = artist.nodeid
        draw_node = self._draw_nodes[nodeid]
        output_node = self._output_nodes[nodeid]
        if self._destination_is_fig:
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


def _get_points_info(artist, figure):
    """
    Convert the raw (x, y) position of a point to a dict containing the dimensions of
    each axis, and scalar values with units.
    """
    return lambda: {
        'x': {
            'dim': figure.dims['x'],
            'value': sc.scalar(artist.x, unit=figure.canvas.xunit)
        },
        'y': {
            'dim': figure.dims['y'],
            'value': sc.scalar(artist.y, unit=figure.canvas.yunit)
        },
    }


def _make_points(**kwargs):
    """
    Intermediate function needed for giving to `partial` to avoid making mpltoolbox a
    hard dependency.
    """
    from mpltoolbox import Points
    return Points(**kwargs)


PointsTool = partial(DrawingTool,
                     tool=partial(_make_points, mec='w'),
                     get_artist_info=_get_points_info,
                     icon='crosshairs')
"""
Tool to add point markers onto a figure.

Parameters
----------
figure:
    The figure where the tool will draw things (points, lines, shapes...).
input_node:
    The node that provides the raw data which is shown in ``figure``.
func:
    The function to be used to make a node whose parents will be the ``input_node``
    and a node yielding the current state of the tool (current position, size).
destination:
    Where the output from the ``func`` node will be then sent on. This can either
    be a figure, or another graph node.
value:
    Activate the tool upon creation if ``True``.
**kwargs:
    Additional arguments are forwarded to the ``ToggleTool`` constructor.
"""
