# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .common import require_interactive_backend, preprocess
from .slicer import Slicer
from ..core import Node, View
from ..core.utils import coord_element_to_string

from functools import partial
import scipp as sc
from numpy import ndarray
from typing import Any, Union, Dict
from matplotlib.colors import to_hex
import uuid


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
        self._data_node = data_node
        self._slider_node = slider_node
        self._fig = fig
        self._lines = {}
        self.button = ipw.Button(description='Save line')
        self.button.on_click(self.save_line)
        self.container = ipw.VBox()
        self.widget = ipw.VBox([self.button, self.container], layout={'width': '350px'})

    def _update_container(self):
        self.container.children = [line['tool'] for line in self._lines.values()]

    def save_line(self, change: Dict[str, Any] = None):
        from ..widgets import ColorTool
        line_id = uuid.uuid4().hex
        data = self._data_node.request_data()
        self._fig.update(data, key=line_id)
        slice_values = self._slider_node.request_data()
        text = ', '.join(f'{k}: {coord_element_to_string(data.meta[k])}'
                         for k, it in slice_values.items())
        line = self._fig.artists[line_id]
        tool = ColorTool(text=text, color=to_hex(line.color))
        self._lines[line_id] = {'line': line, 'tool': tool}
        self._update_container()
        tool.color.observe(partial(self.change_line_color, line_id=line_id),
                           names='value')
        tool.button.on_click(partial(self.remove_line, line_id=line_id))

    def change_line_color(self, change: Dict[str, Any], line_id: str):
        self._lines[line_id]['line'].color = change['new']
        self._fig.canvas.draw()

    def remove_line(self, change: Dict[str, Any], line_id: str):
        self._lines[line_id]['line'].remove()
        self._fig.canvas.draw()
        del self._lines[line_id]
        self._update_container()


def superplot(obj: Union[sc.typing.VariableLike, ndarray],
              keep: str = None,
              *,
              crop: Dict[str, Dict[str, sc.Variable]] = None,
              **kwargs):
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
    crop:
        Set the axis limits. Limits should be given as a dict with one entry per
        dimension to be cropped. Each entry should be a nested dict containing scalar
        values for `'min'` and/or `'max'`. Example:
        `da.plot(crop={'time': {'min': 2 * sc.Unit('s'), 'max': 40 * sc.Unit('s')}})`
    **kwargs:
        See :py:func:`plopp.plot` for the full list of line customization arguments.

    Returns
    -------
    :
        A :class:`Box` which will contain a :class:`Figure`, slider widgets and a tool
        to save/delete lines.
    """
    require_interactive_backend('superplot')
    da = preprocess(obj, crop=crop, ignore_size=True)
    if keep is None:
        keep = da.dims[-1]
    sl = Slicer(da=da, keep=[keep], crop=crop, **kwargs)
    save_tool = LineSaveTool(data_node=sl.slice_node,
                             slider_node=sl.slider_node,
                             fig=sl.fig)
    from ..widgets import Box
    return Box([[sl.fig, save_tool.widget], sl.slider])
