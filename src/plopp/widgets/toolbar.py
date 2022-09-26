# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .tools import ButtonTool, ToggleTool

from ipywidgets import VBox
from functools import partial

TOOL_LIBRARY = {
    'home': partial(ButtonTool, icon="home", tooltip="Autoscale view"),
    'pan': partial(ToggleTool, icon="arrows", tooltip="Pan"),
    'zoom': partial(ToggleTool, icon="search-plus", tooltip="Zoom"),
    'logx': partial(ToggleTool, description="logx", tooltip="Toggle X axis scale"),
    'logy': partial(ToggleTool, description="logy", tooltip="Toggle Y axis scale"),
    'log': partial(ToggleTool, description="log", tooltip="Toggle data norm"),
    'save': partial(ButtonTool, icon="save", tooltip="Save figure")
}


class Toolbar(VBox):
    """
    Custom toolbar with additional buttons for controlling log scales and
    normalization, and with back/forward buttons removed.
    """

    def __init__(self, tools=None):
        self.tools = {}
        if tools is not None:
            for key, callback in tools.items():
                tool = TOOL_LIBRARY[key](callback=callback)
                setattr(self, key, tool)
                self.tools[key] = tool
        super().__init__()
        self._update_children()

    def __getitem__(self, key):
        return self.tools[key]

    def __setitem__(self, key, tool):
        self.tools[key] = tool
        self._update_children()

    def __delitem__(self, key):
        del self.tools[key]
        self._update_children()

    def _update_children(self):
        self.children = [t.widget for t in self.tools.values()]
