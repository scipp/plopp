# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .tools import ButtonTool, ToggleTool, MultiToggleTool

from ipywidgets import VBox, HBox
from functools import partial

TOOL_LIBRARY = {
    'home':
    partial(ButtonTool, icon='home', tooltip='Autoscale view'),
    'panzoom':
    partial(MultiToggleTool,
            options=[('', 'pan'), (' ', 'zoom')],
            icons=['arrows', 'search-plus'],
            tooltips=['Pan', 'Zoom'],
            value=None),
    # 'zoom':
    # partial(ToggleTool, icon='search-plus', tooltip='Zoom'),
    'logx':
    partial(ToggleTool, description='logx', tooltip='Toggle X axis scale'),
    'logy':
    partial(ToggleTool, description='logy', tooltip='Toggle Y axis scale'),
    'lognorm':
    partial(ToggleTool, description='log', tooltip='Toggle colorscale normalization'),
    'save':
    partial(ButtonTool, icon='save', tooltip='Save figure'),
    'box':
    partial(ToggleTool, value=True, icon='codepen',
            tooltip='Toggle outline visibility'),
    'axes':
    partial(ToggleTool,
            value=True,
            description='\u27C0',
            style={'font_weight': 'bold'},
            tooltip='Toggle visibility of XYZ axes'),
    'camerax':
    partial(ButtonTool,
            icon='camera',
            description='X',
            tooltip='Camera to X normal. Click twice to flip the view direction.'),
    'cameray':
    partial(ButtonTool,
            icon='camera',
            description='Y',
            tooltip='Camera to Y normal. Click twice to flip the view direction.'),
    'cameraz':
    partial(ButtonTool,
            icon='camera',
            description='Z',
            tooltip='Camera to Z normal. Click twice to flip the view direction.')
}


class Toolbar(VBox):
    '''
    Custom toolbar with additional buttons for controlling log scales and
    normalization, and with back/forward buttons removed.
    '''

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
        self.children = list(self.tools.values())
