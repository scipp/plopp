# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .common import require_interactive_backend, preprocess
from .figure import figure
from ..core import input_node, widget_node
from ..core.utils import coord_to_string
from ..widgets import ColorTool

from functools import partial
import scipp as sc
from numpy import ndarray
from typing import Union, Dict, Literal
from matplotlib.colors import to_hex
import uuid


class LineSaveTool:

    def __init__(self, data_node, slider_node, fig):
        import ipywidgets as ipw
        self._data_node = data_node
        self._slider_node = slider_node
        self._fig = fig
        self._lines = {}
        self.button = ipw.Button(description='Save line')
        self.button.on_click(self._save_line)
        self.container = ipw.VBox()
        self.widget = ipw.VBox([self.button, self.container], layout={'width': '500px'})

    def _update_container(self):
        self.container.children = [line['tool'] for line in self._lines.values()]

    def _save_line(self, change):
        line_id = uuid.uuid4().hex
        data = self._data_node.request_data()
        self._fig.update(data, key=line_id)
        slice_values = self._slider_node.request_data()
        text = ', '.join(f'{k}: {coord_to_string(data.meta[k])}'
                         for k, it in slice_values.items())
        line = self._fig._children[line_id]
        tool = ColorTool(text=text, color=to_hex(line.color))
        self._lines[line_id] = {'line': line, 'tool': tool}
        self._update_container()
        tool.color.observe(partial(self._change_line_color, line_id=line_id),
                           names='value')
        tool.button.on_click(partial(self._remove_line, line_id=line_id))

    def _change_line_color(self, change, line_id):
        self._lines[line_id].color = change.new
        self._fig.draw()

    def _remove_line(self, change, line_id):
        self._lines[line_id]['line'].remove()
        self._fig.draw()
        del self._lines[line_id]
        self._update_container()


def superplot(obj: Union[sc.typing.VariableLike, ndarray],
              keep: str = None,
              *,
              operation: Literal['sum', 'mean', 'min', 'max'] = 'sum',
              crop: Dict[str, Dict[str, sc.Variable]] = None,
              **kwargs):
    """
    """
    require_interactive_backend('slicer')

    from plopp.widgets import SliceWidget, slice_dims, Box
    da = preprocess(obj, crop=crop, ignore_size=True)
    a = input_node(da)

    if keep is None:
        keep = da.dims[-1]
    sl = SliceWidget(da, dims=list(set(da.dims) - set([keep])))
    w = widget_node(sl)
    slice_node = slice_dims(a, w)
    fig = figure(slice_node, **{**{'crop': crop}, **kwargs})
    save_tool = LineSaveTool(data_node=slice_node, slider_node=w, fig=fig)
    return Box([[fig, save_tool.widget], sl])
