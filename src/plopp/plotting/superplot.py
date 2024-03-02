# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from functools import partial
from typing import Any, Dict, Optional

from matplotlib.colors import to_hex

from ..core import Node, View
from ..core.typing import Plottable
from ..core.utils import coord_element_to_string
from .common import require_interactive_backend
from .slicer import Slicer


class LineSaveTool:
    """
    Create a tool that is used to copy and save the currently displayed 1D line on a
    plot.

    Parameters
    ----------
    data_node:
        The node that generates the input data.
    """

    def __init__(self, data_node: Node, slider_node: Node, fig: View):
        import ipywidgets as ipw

        from ..widgets.box import VBar

        self._data_node = data_node
        self._slider_node = slider_node
        self._fig = fig
        self._lines = {}
        self.button = ipw.Button(description='Save line')
        self.button.on_click(self.save_line)
        self.container = VBar()
        self.widget = VBar([self.button, self.container], layout={'width': '350px'})

    def _update_container(self):
        self.container.children = [line['tool'] for line in self._lines.values()]

    def save_line(self, change: Dict[str, Any] = None):
        from ..widgets import ColorTool

        data = self._data_node.request_data()
        node = Node(data)
        node.name = f'Save node {len(self._lines)}'
        line_id = node._id
        node.add_view(self._fig._view)
        self._fig._view.render()
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

    def change_line_color(self, change: Dict[str, Any], line_id: str):
        self._lines[line_id]['line'].color = change['new']

    def remove_line(self, change: Dict[str, Any], line_id: str):
        self._lines[line_id]['line'].remove()
        self._lines[line_id]['node'].remove()
        del self._lines[line_id]
        self._update_container()


class Superplot:
    """
    Class that slices all but one dimension of the input, with a slider per sliced
    dimension, below the figure.
    It also has a ``LineSaveTool`` for saving the currently displayed line.

    Note:

    This class primarily exists to facilitate unit testing. When running unit tests, we
    are not in a Jupyter notebook, and the generated figures are not widgets that can
    be placed in the `Box` widget container at the end of the `superplot` function.
    We therefore place most of the code for creating a Superplot in this class, which is
    under unit test coverage. The thin `superplot` wrapper is not covered by unit tests.

    Parameters
    ----------
    obj:
        The object to be plotted.
    keep:
        The single dimension to be kept, all remaining dimensions will be sliced.
        This should be a single string. If no dim is provided, the last/inner dim will
        be kept.
    **kwargs:
        See :py:func:`plopp.plot` for the full list of line customization arguments.
    """

    def __init__(
        self,
        obj: Plottable,
        keep: Optional[str] = None,
        **kwargs,
    ):
        self.slicer = Slicer(obj, keep=keep, **kwargs)
        self.linesavetool = LineSaveTool(
            data_node=self.slicer.slice_nodes[0],
            slider_node=self.slicer.slider_node,
            fig=self.slicer.figure,
        )
        self.figure = self.slicer.figure
        self.slider = self.slicer.slider


def superplot(
    obj: Plottable,
    keep: Optional[str] = None,
    **kwargs,
):
    """
    Plot a multi-dimensional object as a one-dimensional line, slicing all but one
    dimension. This will produce one slider per sliced dimension, below the figure.
    In addition, a tool for saving the currently displayed line is added on the right
    hand side of the figure.

    Parameters
    ----------
    obj:
        The object to be plotted.
    keep:
        The single dimension to be kept, all remaining dimensions will be sliced.
        This should be a single string. If no dim is provided, the last/inner dim will
        be kept.
    **kwargs:
        See :py:func:`plopp.plot` for the full list of line customization arguments.

    Returns
    -------
    :
        A :class:`widgets.Box` which will contain a :class:`graphics.FigLine`, slider
        widgets and a tool to save/delete lines.
    """
    require_interactive_backend('superplot')
    slicer = Slicer(obj, keep=keep, **kwargs)
    linesavetool = LineSaveTool(
        data_node=slicer.slice_nodes[0],
        slider_node=slicer.slider_node,
        fig=slicer.figure,
    )
    slicer.figure.right_bar.add(linesavetool.widget)
    # self.slider = self.slicer.slider

    # sp = Superplot(obj=obj, keep=keep, **kwargs)
    # from ..widgets import Box

    # return Box([[sp.figure, sp.linesavetool.widget], sp.slider])
    return slicer.figure
