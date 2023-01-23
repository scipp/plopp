# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from typing import Any, Dict, Optional

from ipywidgets import VBox

from ..graphics import ColorMapper
from . import tools


class Toolbar(VBox):
    """
    Custom toolbar to control interactive figures.

    Parameters
    ----------
    tools:
        Dictionary of tools to populate the toolbar.
    """

    def __init__(self, tools: Dict[str, Any] = None):
        self.tools = {}
        if tools is not None:
            for key, tool in tools.items():
                setattr(self, key, tool.callback)
                self.tools[key] = tool

        super().__init__()
        self._update_children()

    def __getitem__(self, key: str) -> Any:
        return self.tools[key]

    def __setitem__(self, key: str, tool: Any):
        self.tools[key] = tool
        self._update_children()

    def __delitem__(self, key: str):
        del self.tools[key]
        self._update_children()

    def _update_children(self):
        self.children = list(self.tools.values())


def make_toolbar_canvas2d(canvas: Any,
                          colormapper: Optional[ColorMapper] = None) -> Toolbar:
    """
    Create a toolbar for a 2D canvas.
    If the colormapper is defined, add a button to toggle the norm of the colormapper.

    Parameters
    ----------
    canvas:
        The 2D canvas to operate on.
    colormapper:
        The colormapper which controls the colors of the artists in the canvas (for
        image plots).
    """
    tool_list = {
        'home': tools.HomeTool(canvas.autoscale),
        'panzoom': tools.PanZoomTool(canvas.panzoom),
        'logx': tools.LogxTool(canvas.logx, value=canvas.xscale == 'log'),
        'logy': tools.LogyTool(canvas.logy, value=canvas.yscale == 'log'),
    }
    if colormapper is not None:
        tool_list['lognorm'] = tools.LogNormTool(colormapper.toggle_norm,
                                                 value=colormapper.norm == 'log')
    tool_list['save'] = tools.SaveTool(canvas.download_figure)
    return Toolbar(tools=tool_list)


def make_toolbar_canvas3d(canvas: Any,
                          colormapper: Optional[ColorMapper] = None) -> Toolbar:
    """
    Create a toolbar for a 3D canvas.
    If the colormapper is defined, add a button to toggle the norm of the colormapper.

    Parameters
    ----------
    canvas:
        The 3D canvas to operate on.
    colormapper:
        The colormapper which controls the colors of the artists in the canvas.
    """
    tool_list = {
        'home':
        tools.HomeTool(canvas.home),
        'camerax':
        tools.CameraTool(canvas.camera_x_normal,
                         description='X',
                         tooltip='Camera to X normal. '
                         'Click twice to flip the view direction.'),
        'cameray':
        tools.CameraTool(canvas.camera_y_normal,
                         description='Y',
                         tooltip='Camera to Y normal. '
                         'Click twice to flip the view direction.'),
        'cameraz':
        tools.CameraTool(canvas.camera_z_normal,
                         description='Z',
                         tooltip='Camera to Z normal. '
                         'Click twice to flip the view direction.')
    }
    if colormapper is not None:
        tool_list['lognorm'] = tools.LogNormTool(colormapper.toggle_norm,
                                                 value=colormapper.norm == 'log')
    tool_list.update({
        'box': tools.OutlineTool(canvas.toggle_outline),
        'axes': tools.AxesTool(canvas.toggle_axes3d)
    })
    return Toolbar(tools=tool_list)
