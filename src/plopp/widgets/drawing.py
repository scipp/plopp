# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from collections.abc import Callable
from functools import partial
from typing import Any

import scipp as sc

from ..core import Node, node
from ..core.typing import FigureLike
from ..graphics import BaseFig
from .tools import ToggleTool


def is_figure(x):
    answer = isinstance(x, BaseFig)
    return answer


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
    continuous_update:
        If ``True``, the tool will update the nodes as a drawing object changes.
        If ``False``, destination will be updated only when the user releases the
        mouse button.
        In other words, it can be set ``True`` for tools that need fast feedback,
        or ``False`` for tools that use computationally expensive functions.

    **kwargs:
        Additional arguments are forwarded to the ``ToggleTool`` constructor.
    """

    def __init__(
        self,
        figure: FigureLike,
        input_node: Node,
        tool: Any,
        func: Callable,
        destination: FigureLike | Node,
        get_artist_info: Callable,
        value: bool = False,
        continuous_update: bool = True,
        **kwargs,
    ):
        super().__init__(callback=self.start_stop, value=value, **kwargs)

        self._figure = figure
        self._input_node = input_node
        self._draw_nodes = {}
        self._output_nodes = {}
        self._func = func
        self._tool = tool(ax=self._figure.ax, autostart=False)
        self._destination = destination
        self._destination_is_fig = is_figure(self._destination)
        self._get_artist_info = get_artist_info
        self._get_artist_info_is_callable = None
        self._tool.on_create(self.make_node)
        self._tool.on_remove(self.remove_node)
        if continuous_update:
            self._tool.on_change(self.update_node)
        else:
            self._tool.on_vertex_release(self.update_node)
            self._tool.on_drag_release(self.update_node)

    def make_node(self, artist):
        info = self._get_artist_info(artist=artist, figure=self._figure)
        if self._get_artist_info_is_callable is None:
            self._get_artist_info_is_callable = callable(info)
        draw_node = Node(info)
        draw_node.pretty_name = f'Draw node {len(self._draw_nodes)}'
        nodeid = draw_node.id
        self._draw_nodes[nodeid] = draw_node
        artist.nodeid = nodeid
        output_node = node(self._func)(self._input_node, draw_node)
        output_node.pretty_name = f'Output node {len(self._output_nodes)}'
        self._output_nodes[nodeid] = output_node
        if self._destination_is_fig:
            output_node.add_view(self._destination.view)
            self._destination.update({output_node.id: output_node()})
            self._destination.artists[output_node.id].color = (
                artist.color if hasattr(artist, 'color') else artist.edgecolor
            )
        elif isinstance(self._destination, Node):
            self._destination.add_parents(output_node)
            self._destination.notify_children(artist)

    def update_node(self, artist):
        n = self._draw_nodes[artist.nodeid]
        if self._get_artist_info_is_callable:
            n.func = self._get_artist_info(artist=artist, figure=self._figure)
        else:
            n.func = partial(self._get_artist_info, artist=artist, figure=self._figure)
        n.notify_children(artist)

    def remove_node(self, artist):
        nodeid = artist.nodeid
        draw_node = self._draw_nodes.pop(nodeid)
        output_node = self._output_nodes[nodeid]
        if self._destination_is_fig:
            self._destination.artists[output_node.id].remove()
            del self._destination.artists[output_node.id]
            self._destination.canvas.draw()
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


class PolygonTool(ToggleTool):
    """
    Tool to draw polygons on a figure and use them to generate derived data.

    Parameters
    ----------
    figure:
        The figure where the tool will draw polygons.
    input_node:
        The node that provides the raw data which is shown in ``figure``.
    func:
        The function to be used to make a node whose parents will be the
        ``input_node`` and a node yielding the polygon vertices.
    destination:
        Where the output from the ``func`` node will be then sent on. This can
        either be a figure, or another graph node.
    get_vertices_info:
        A function that converts polygon vertices to a dict usable by ``func``.
    value:
        Activate the tool upon creation if ``True``.

    **kwargs:
        Additional arguments are forwarded to the ``ToggleTool`` constructor.
    """

    def __init__(
        self,
        figure: FigureLike,
        input_node: Node,
        func: Callable,
        destination: FigureLike | Node,
        get_vertices_info: Callable,
        value: bool = False,
        **kwargs,
    ):
        super().__init__(callback=self.start_stop, value=value, **kwargs)

        self._figure = figure
        self._input_node = input_node
        self._func = func
        self._destination = destination
        self._destination_is_fig = is_figure(self._destination)
        self._get_vertices_info = get_vertices_info
        self._selector = None
        self._polygons = {}
        self._patch_to_nodeid = {}
        self._draw_nodes = {}
        self._output_nodes = {}
        self._pick_cid = None

    def _ensure_selector(self):
        if self._selector is not None:
            return
        from matplotlib.widgets import PolygonSelector

        self._selector = PolygonSelector(
            self._figure.ax,
            onselect=self._on_select,
            useblit=False,
            props={"linewidth": 1.5, "linestyle": "-", "alpha": 0.8},
        )
        self._pick_cid = self._figure.canvas.fig.canvas.mpl_connect(
            "pick_event", self._on_pick
        )

    def _on_select(self, verts):
        if len(verts) < 3:
            return
        info = self._get_vertices_info(verts=verts, figure=self._figure)
        draw_node = Node(info)
        draw_node.pretty_name = f'Polygon draw node {len(self._draw_nodes)}'
        nodeid = draw_node.id
        self._draw_nodes[nodeid] = draw_node
        output_node = node(self._func)(self._input_node, draw_node)
        output_node.pretty_name = f'Polygon output node {len(self._output_nodes)}'
        self._output_nodes[nodeid] = output_node
        if self._destination_is_fig:
            output_node.add_view(self._destination.view)
            self._destination.update({output_node.id: output_node()})
        elif isinstance(self._destination, Node):
            self._destination.add_parents(output_node)
            self._destination.notify_children(verts)

        from matplotlib.patches import Polygon

        patch = Polygon(
            verts, closed=True, fill=False, linewidth=1.5, zorder=4, picker=True
        )
        if self._destination_is_fig:
            patch.set_edgecolor(self._destination.artists[output_node.id].color)
        self._figure.ax.add_patch(patch)
        self._polygons[nodeid] = patch
        self._patch_to_nodeid[patch] = nodeid
        self._figure.canvas.draw()

        if self._selector is not None:
            self._selector.clear()

    def _on_pick(self, event):
        if event.mouseevent.button != 3:
            return
        if self.value:
            return
        nodeid = self._patch_to_nodeid.get(event.artist)
        if nodeid is None:
            return
        self.remove(nodeid)

    def remove(self, nodeid):
        patch = self._polygons.pop(nodeid)
        self._patch_to_nodeid.pop(patch, None)
        if self._destination_is_fig:
            artist = self._destination.artists.pop(self._output_nodes[nodeid].id)
            artist.remove()
            self._destination.canvas.draw()
        patch.remove()
        output_node = self._output_nodes.pop(nodeid)
        output_node.remove()
        draw_node = self._draw_nodes.pop(nodeid)
        draw_node.remove()
        self._figure.canvas.draw()

    def start_stop(self):
        """
        Toggle start or stop of the tool.
        """
        if self.value:
            self._ensure_selector()
            self._selector.set_active(True)
        elif self._selector is not None:
            self._selector.set_active(False)


def _get_points_info(artist, figure):
    """
    Convert the raw (x, y) position of a point to a dict containing the dimensions of
    each axis, and scalar values with units.
    """
    return {
        'x': {
            'dim': figure.canvas.dims['x'],
            'value': sc.scalar(artist.x, unit=figure.canvas.units['x']),
        },
        'y': {
            'dim': figure.canvas.dims['y'],
            'value': sc.scalar(artist.y, unit=figure.canvas.units['y']),
        },
    }


def _get_polygon_info(verts, figure):
    """
    Convert the raw polygon vertices to a dict containing the dimensions of
    each axis, and arrays with units.
    """
    xs, ys = zip(*verts, strict=True)
    return {
        'x': {
            'dim': figure.canvas.dims['x'],
            'value': sc.array(
                dims=['vertex'],
                values=xs,
                unit=figure.canvas.units['x'],
            ),
        },
        'y': {
            'dim': figure.canvas.dims['y'],
            'value': sc.array(
                dims=['vertex'],
                values=ys,
                unit=figure.canvas.units['y'],
            ),
        },
    }


def _make_points(**kwargs):
    """
    Intermediate function needed for giving to `partial` to avoid making mpltoolbox a
    hard dependency.
    """
    from mpltoolbox import Points

    return Points(**kwargs)


PointsTool = partial(
    DrawingTool,
    tool=partial(_make_points, mec='w'),
    get_artist_info=_get_points_info,
    icon='crosshairs',
)
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
