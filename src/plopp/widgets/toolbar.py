# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from typing import Any

from ipywidgets import VBox

from ..graphics import GraphicalView
from . import tools


class Toolbar(VBox):
    """
    Custom toolbar to control interactive figures.

    Parameters
    ----------
    tools:
        Dictionary of tools to populate the toolbar.
    """

    def __init__(self, tools: dict[str, Any] | None = None):
        self.tools = {}
        if tools is not None:
            for key, tool in tools.items():
                if isinstance(tool.callback, dict):
                    for name, cb in tool.callback.items():
                        setattr(self, name, cb)
                else:
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


def make_toolbar_canvas2d(view: GraphicalView) -> Toolbar:
    """
    Create a toolbar for a 2D canvas.
    If the colormapper is defined, add a button to toggle the norm of the colormapper.

    Parameters
    ----------
    view:
        The 2D view to operate on.
    """

    def logx() -> None:
        view.canvas.logx()
        view.autoscale()
        view.canvas.draw()

    def logy() -> None:
        view.canvas.logy()
        view.autoscale()
        view.canvas.draw()

    def autoscale_axes() -> None:
        view.autoscale()
        view.canvas.draw()

    def autoscale_colors() -> None:
        view.colormapper.autoscale()
        view.canvas.draw()

    tool_list = {
        "home": tools.HomeTool(autoscale_axes, tooltip="Autoscale axes range"),
        "panzoom": tools.PanZoomTool(view.canvas.panzoom),
        "logx": tools.LogxTool(logx, value=view.canvas.xscale == "log"),
        "logy": tools.LogyTool(logy, value=view.canvas.yscale == "log"),
        "save": tools.SaveTool(view.canvas.download_figure),
    }
    if view.colormapper is not None:
        tool_list.update(
            {
                "lognorm": tools.LogNormTool(
                    view.colormapper.toggle_norm, value=view.colormapper.norm == "log"
                ),
                "autoscale": tools.AutoscaleTool(autoscale_colors),
            }
        )
    order = ["home", "autoscale", "panzoom", "logx", "logy", "lognorm", "save"]
    return Toolbar(tools={key: tool_list[key] for key in order if key in tool_list})


def make_toolbar_canvas3d(view: GraphicalView) -> Toolbar:
    """
    Create a toolbar for a 3D canvas.
    If the colormapper is defined, add a button to toggle the norm of the colormapper.

    Parameters
    ----------
    view:
        The 3D view to operate on.
    """

    def autoscale_colors() -> None:
        view.colormapper.autoscale()
        view.canvas.draw()

    tool_list = {
        "home": tools.HomeTool(view.canvas.home, tooltip="Reset camera"),
        "autoscale": tools.AutoscaleTool(autoscale_colors),
        "camerax": tools.CameraTool(
            view.canvas.camera_x_normal,
            description="X",
            tooltip="Camera to X normal. Click twice to flip the view direction.",
        ),
        "cameray": tools.CameraTool(
            view.canvas.camera_y_normal,
            description="Y",
            tooltip="Camera to Y normal. Click twice to flip the view direction.",
        ),
        "cameraz": tools.CameraTool(
            view.canvas.camera_z_normal,
            description="Z",
            tooltip="Camera to Z normal. Click twice to flip the view direction.",
        ),
    }
    if view.colormapper is not None:
        tool_list["lognorm"] = tools.LogNormTool(
            view.colormapper.toggle_norm, value=view.colormapper.norm == "log"
        )
    tool_list.update(
        {
            "box": tools.OutlineTool(view.canvas.toggle_outline),
            "axes": tools.AxesTool(view.canvas.toggle_axes3d),
            "size": tools.PlusMinusTool(
                plus={
                    "callback": view.canvas.bigger,
                    "tooltip": "Increase canvas size",
                },
                minus={
                    "callback": view.canvas.smaller,
                    "tooltip": "Decrease canvas size",
                },
            ),
        }
    )
    return Toolbar(tools=tool_list)
