# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

# from .common import require_interactive_backend, preprocess
# from .figure import figure1d, figure2d
from ..core import input_node, node, Node, View
from ..core.utils import coord_as_bin_edges
from .tools import DrawLinesTool

import scipp as sc
from numpy import ndarray
from typing import Any, Union, Dict, Literal
from scipy.interpolate import interp2d
import numpy as np


def make_cut(xy, interpolator):
    x1 = xy['x'][0]
    y1 = xy['y'][0]
    x2 = xy['x'][1]
    y2 = xy['y'][1]

    num_points = 100
    xvalues = np.linspace(x1, x2, num_points)
    yvalues = np.linspace(y1, y2, num_points)

    profile = np.array([interpolator(x, y)[0] for x, y in zip(xvalues, yvalues)])
    out = sc.DataArray(data=sc.array(dims=['distance'], values=profile),
                       coords={
                           'distance':
                           sc.array(dims=['distance'],
                                    values=np.linalg.norm(
                                        [xvalues - xvalues[0], yvalues - yvalues[0]],
                                        axis=0))
                       })
    return out


class LineCutTool(DrawLinesTool):
    """
    """

    def __init__(self, fig2d: View, fig1d: View):
        if len(fig2d.graph_nodes) > 1:
            raise ValueError("Cannot automatically generate tool because figure has "
                             "more than one artist.")
        self._data_array = list(fig2d.graph_nodes.values())[0].request_data()
        self._interpolator = interp2d(self._data_array.coords['xx'].values,
                                      self._data_array.coords['yy'].values,
                                      self._data_array.values)

        # self._root_node = root_node
        self._fig1d = fig1d
        self._event_nodes = {}
        # self._cutting_nodes = {}
        # self._xdim = fig2d.dims['x']['dim']
        # self._ydim = fig2d.dims['y']['dim']

        # self.cuts = tbx.Lines(ax=fig2d.canvas.ax, n=2)
        super().__init__(ax=fig2d.canvas.ax, n=2)
        # self.cuts = PointsTool(ax=f2d.canvas.ax, tooltip='Add inspector points')
        self.lines.on_create = self.make_node
        # self.lines.points.on_vertex_move = self.update_node
        self.lines.on_remove = self.remove_node
        # f2d.toolbar['inspect'] = pts

    def make_node(self, change: Dict[str, Any]):
        from ..widgets import slice_dims
        # event = change['event']
        line_data = change['artist'].get_xydata()
        draw_node = Node(lambda: {'x': line_data[:, 0], 'y': line_data[:, 1]})
        self._event_nodes[draw_node.id] = draw_node
        change['artist'].nodeid = draw_node.id
        cut_node = node(make_cut, interpolator=self._interpolator)(xy=draw_node)
        cut_node.add_view(self._fig1d)
        # self._cutting_nodes[cut_node.id] =
        self._fig1d.update(new_values=cut_node.request_data(), key=cut_node.id)

    # def update_node(self, change: Dict[str, Any]):
    #     event = change['event']
    #     n = self._event_nodes[change['artist'].nodeid]
    #     n.func = lambda: {
    #         self._xdim: sc.scalar(event.xdata,
    #                               unit=self._data_array.meta[self._xdim].unit),
    #         self._ydim: sc.scalar(event.ydata,
    #                               unit=self._data_array.meta[self._ydim].unit)
    #     }
    #     n.notify_children(change)

    def remove_node(self, change: Dict[str, Any]):
        n = self._event_nodes[change['artist'].nodeid]
        pnode = n.children[0]
        self._fig1d.artists[pnode.id].remove()
        self._fig1d.canvas.draw()
        pnode.remove()
        n.remove()