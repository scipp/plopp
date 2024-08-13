# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from functools import partial
from typing import Any

import ipywidgets as ipw
from matplotlib.colors import to_hex

from ..core import Node, View
from ..core.utils import coord_element_to_string
from .box import VBar


class LineSaveTool(VBar):
    """
    Create a tool that is used to copy and save the currently displayed 1D line on a
    plot.

    Parameters
    ----------
    data_node:
        The node that generates the input data.
    slider_node:
        The node that generates the sliced data.
    fig:
        The figure to which the lines are to be added.
    """

    def __init__(self, data_node: Node, slider_node: Node, fig: View):
        self._data_node = data_node
        self._slider_node = slider_node
        self._fig = fig
        self._lines = {}
        self.button = ipw.Button(description='Save line')
        self.button.on_click(self.save_line)
        self.container = VBar()
        super().__init__([self.button, self.container], layout={'width': '350px'})

    def _update_container(self):
        self.container.children = [line['tool'] for line in self._lines.values()]

    def save_line(self, change: dict[str, Any] | None = None):
        from ..widgets import ColorTool

        data = self._data_node.request_data()
        node = Node(data)
        node.name = f'Save node {len(self._lines)}'
        line_id = node._id
        node.add_view(self._fig.view)
        self._fig.view.render()
        text = ', '.join(
            f'{k}: {coord_element_to_string(data.coords[k])}'
            for k in self._slider_node.request_data()
        )
        line = self._fig.artists[line_id]
        tool = ColorTool(text=text, color=to_hex(line.color))
        self._lines[line_id] = {'line': line, 'tool': tool, 'node': node}
        self._update_container()
        tool.color.observe(
            partial(self.change_line_color, line_id=line_id), names='value'
        )
        tool.button.on_click(partial(self.remove_line, line_id=line_id))

    def change_line_color(self, change: dict[str, Any], line_id: str):
        self._lines[line_id]['line'].color = change['new']

    def remove_line(self, change: dict[str, Any], line_id: str):
        self._lines[line_id]['line'].remove()
        self._lines[line_id]['node'].remove()
        del self._lines[line_id]
        self._update_container()
