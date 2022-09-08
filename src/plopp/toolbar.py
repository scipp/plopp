# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

# import ipywidgets as ipw

from dataclasses import dataclass
from functools import partial
from typing import Any, Callable

from .displayable import Displayable

STYLE_LAYOUT = {"layout": {"width": "34px", "padding": "0px 0px 0px 0px"}}

# @dataclass
# class Tool:
#     """Class for keeping track of an item in inventory."""
#     widget: Any
#     callback: Callable

#     def __call__(self, *args, **kwargs):
#         return self.callback(*args, **kwargs)


class ButtonTool:

    def __init__(self, callback: Callable = None, **kwargs):
        """
        Create a new button and add it to the toolbar members list.
        """
        from ipywidgets import Button
        self.widget = Button(**{**STYLE_LAYOUT, **kwargs})
        self._callback = callback
        self.widget.on_click(self._execute)
        # return Tool(widget=b, callback=callback)

    def __call__(self, *args, **kwargs):
        self.widget.click()

    def _execute(self, *args, **kwargs):
        self._callback()


class ToggleTool:

    def __init__(self, callback: Callable, value: bool = False, **kwargs):
        """
        """
        from ipywidgets import Button
        self.widget = Button(**{**STYLE_LAYOUT, **kwargs})
        self._callback = callback
        self.widget.on_click(self._execute)
        # return Tool(widget=tb, callback=callback)

    def __call__(self):
        # if disconnect:
        #     self.widget.unobserve_all()
        self.widget.value = not self.widget.value
        # if disconnect:
        #     self.widget.observe(self._execute, names='value')

    def _execute(self, *args, **kwargs):
        self._callback()


TOOL_LIBRARY = {
    'home': partial(ButtonTool, icon="home", tooltip="Autoscale view"),
    'pan': partial(ToggleTool, icon="arrows", tooltip="Pan"),
    'zoom': partial(ToggleTool, icon="search-plus", tooltip="Zoom"),
    'logx': partial(ToggleTool, description="logx", tooltip="Toggle X axis scale"),
    'logy': partial(ToggleTool, description="logy", tooltip="Toggle Y axis scale"),
    'save': partial(ButtonTool, icon="save", tooltip="Save figure")
}
# class ToggleButtons(ipw.ToggleButtons):

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.on_msg(self._reset)
#         self._current_value = self.value

#     def _reset(self, *ignored):
#         """
#         If the currently selected button is clicked again, set value to None.
#         """
#         if self.value == self._current_value:
#             self.value = None
#         self._current_value = self.value


class Toolbar(Displayable):
    """
    Custom toolbar with additional buttons for controlling log scales and
    normalization, and with back/forward buttons removed.
    """

    def __init__(self, tools=None):
        # self._dims = None
        # self.controller = None
        self._widgets = {}
        for key, callback in tools.items():
            tool = TOOL_LIBRARY[key](callback=callback)
            setattr(self, key, tool)
            self._widgets[key] = tool.widget

        # if 'home' in tools:
        #     self.home =

    def to_widget(self):
        """
        Return the VBox container
        """
        from ipywidgets import VBox
        return VBox(tuple(self._widgets.values()))

    # def add_button(self, name: str, callback: Callable, **kwargs):
    #     """
    #     Create a new button and add it to the toolbar members list.
    #     """
    #     button = ipw.Button(**self._parse_button_args(**kwargs))
    #     button.on_click(callback)
    #     self.members[name] = button

    # def add_togglebutton(self,
    #                      name: str,
    #                      callback: Callable,
    #                      value: bool = False,
    #                      **kwargs):
    #     """
    #     Create a fake ToggleButton using Button because sometimes we want to
    #     change the value of the button without triggering an update, e.g. when
    #     we swap the axes.
    #     """
    #     button = ipw.ToggleButton(layout={
    #         "width": "34px",
    #         "padding": "0px 0px 0px 0px"
    #     },
    #                               value=value,
    #                               **kwargs)
    #     button.observe(callback, names='value')
    #     self.members[name] = button

    # # def add_togglebuttons(self, name: str, callback: Callable, value=None, **kwargs):
    # #     """
    # #     Create a fake ToggleButton using Button because sometimes we want to
    # #     change the value of the button without triggering an update, e.g. when
    # #     we swap the axes.
    # #     """
    # #     buttons = ToggleButtons(button_style='',
    # #                             layout={
    # #                                 "width": "34px",
    # #                                 "padding": "0px 0px 0px 0px"
    # #                             },
    # #                             style={
    # #                                 "button_width": "20px",
    # #                                 "button_padding": "0px 0px 0px 0px"
    # #                             },
    # #                             value=value,
    # #                             **kwargs)
    # #     buttons.observe(callback, names='value')
    # #     self.members[name] = buttons

    # # def _parse_button_args(self, layout: dict = None, **kwargs) -> dict:
    # #     """
    # #     Parse button arguments and add some default styling options.
    # #     """
    # #     args = {"layout": {"width": "34px", "padding": "0px 0px 0px 0px"}}
    # #     if layout is not None:
    # #         args["layout"].update(layout)
    # #     for key, value in kwargs.items():
    # #         if value is not None:
    # #             args[key] = value
    # #     return args
