# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core import node, Node, View
from ..core.utils import coord_as_midpoints
from ..graphics.fig2d import Figure2d
from .tools import DrawLinesTool

from functools import partial
import numpy as np
import scipp as sc
from scipy.interpolate import interp2d
from typing import Any, Dict, Optional


def interpolator(xy, interp_func, resolution, data_unit, distance_unit):
    x1 = xy['x'][0]
    y1 = xy['y'][0]
    x2 = xy['x'][1]
    y2 = xy['y'][1]

    xvalues = np.linspace(x1, x2, resolution)
    yvalues = np.linspace(y1, y2, resolution)

    profile = np.array([interp_func(x, y)[0] for x, y in zip(xvalues, yvalues)])
    out = sc.DataArray(data=sc.array(dims=['distance'], values=profile, unit=data_unit),
                       coords={
                           'distance':
                           sc.array(dims=['distance'],
                                    values=np.linalg.norm(
                                        [xvalues - xvalues[0], yvalues - yvalues[0]],
                                        axis=0),
                                    unit=distance_unit)
                       })
    return out


class LineCutTool(DrawLinesTool):
    """
    Tool to draw cuts/profiles of a 2d data array along a arbitrary lines.

      - When a line is added to the 2d figure, make a new cut in the 1d figure.
      - When a line or one of its vertices is dragged on the 2d figure, update the
        corresponding cut in the 1d figure.
      - When a line is removed from the 2d figure, remove the corresponding cut from
        the 1d figure.
    """

    def __init__(self,
                 figure: View,
                 fig1d: View,
                 data: Optional[sc.DataArray] = None,
                 resolution: int = 100):
        if not isinstance(figure, Figure2d):
            raise TypeError("The line cut tool is only designed to work on 2d figures.")
        if data is None:
            if len(figure.graph_nodes) > 1:
                raise ValueError("Cannot automatically generate tool because figure "
                                 "has more than one artist.")
            data = list(figure.graph_nodes.values())[0].request_data()
        self._data_array = data
        if (self._data_array.coords[figure.dims['x']].unit == self._data_array.coords[
                figure.dims['y']].unit):
            distance_unit = self._data_array.coords[figure.dims['x']].unit
        else:
            distance_unit = ''
        self._interpolator = partial(
            interpolator,
            interp_func=interp2d(
                coord_as_midpoints(self._data_array, key=figure.dims['x']).values,
                coord_as_midpoints(self._data_array, key=figure.dims['y']).values,
                self._data_array.values),
            resolution=resolution,
            data_unit=self._data_array.unit,
            distance_unit=distance_unit)

        self._fig1d = fig1d
        self._event_nodes = {}
        super().__init__(figure=figure, n=2)
        self.lines.on_create = self.make_node
        self.lines.on_vertex_release = self.update_node
        self.lines.on_drag_release = self.update_node
        self.lines.on_remove = self.remove_node

    def make_node(self, change: Dict[str, Any]):
        line_data = change['artist'].get_xydata()
        draw_node = Node(lambda: {'x': line_data[:, 0], 'y': line_data[:, 1]})
        self._event_nodes[draw_node.id] = draw_node
        change['artist'].nodeid = draw_node.id
        cut_node = node(self._interpolator)(xy=draw_node)
        cut_node.add_view(self._fig1d)
        self._fig1d.update(new_values=cut_node.request_data(), key=cut_node.id)
        self._fig1d.artists[cut_node.id].color = change['artist'].get_color()

    def update_node(self, change: Dict[str, Any]):
        line_data = change['artist'].get_xydata()
        n = self._event_nodes[change['artist'].nodeid]
        n.func = lambda: {'x': line_data[:, 0], 'y': line_data[:, 1]}
        n.notify_children(change)

    def remove_node(self, change: Dict[str, Any]):
        n = self._event_nodes[change['artist'].nodeid]
        pnode = n.children[0]
        self._fig1d.artists[pnode.id].remove()
        self._fig1d.canvas.draw()
        pnode.remove()
        n.remove()
