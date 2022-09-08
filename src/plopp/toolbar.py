# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from functools import partial
from typing import Callable

from .displayable import Displayable

LAYOUT_STYLE = {"layout": {"width": "34px", "padding": "0px 0px 0px 0px"}}


class ButtonTool:

    def __init__(self, callback: Callable = None, **kwargs):
        """
        Create a new button with a callback that is called when the button is clicked.
        """
        from ipywidgets import Button
        self.widget = Button(**{**LAYOUT_STYLE, **kwargs})
        self._callback = callback
        self.widget.on_click(self)

    def __call__(self, *args, **kwargs):
        self._callback()


class ToggleTool:

    def __init__(self, callback: Callable, value: bool = False, **kwargs):
        """
        Create a toggle button with a callback that is called when the button is
        toggled. We use a Button and handle the styling ourselves because in some
        cases, we need to toggle the button color without triggering the callback
        function.
        """
        from ipywidgets import Button
        self.widget = Button(**{**LAYOUT_STYLE, **kwargs})
        self._callback = callback
        self.widget.on_click(self)
        self._value = value

    def __call__(self, *args, **kwargs):
        self._toggle()
        self._callback()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val
        self._update_color()

    def _update_color(self):
        self.widget.button_style = 'info' if self._value else ''

    def _toggle(self):
        self._value = not self._value
        self._update_color()


TOOL_LIBRARY = {
    'home': partial(ButtonTool, icon="home", tooltip="Autoscale view"),
    'pan': partial(ToggleTool, icon="arrows", tooltip="Pan"),
    'zoom': partial(ToggleTool, icon="search-plus", tooltip="Zoom"),
    'logx': partial(ToggleTool, description="logx", tooltip="Toggle X axis scale"),
    'logy': partial(ToggleTool, description="logy", tooltip="Toggle Y axis scale"),
    'save': partial(ButtonTool, icon="save", tooltip="Save figure")
}


class Toolbar(Displayable):
    """
    Custom toolbar with additional buttons for controlling log scales and
    normalization, and with back/forward buttons removed.
    """

    def __init__(self, tools=None):
        self._widgets = {}
        for key, callback in tools.items():
            tool = TOOL_LIBRARY[key](callback=callback)
            setattr(self, key, tool)
            self._widgets[key] = tool.widget

    def to_widget(self):
        """
        Return the VBox container
        """
        from ipywidgets import VBox
        return VBox(tuple(self._widgets.values()))
