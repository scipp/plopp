# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .styling import BUTTON_LAYOUT

import ipywidgets as ipw
from typing import Callable

# class ArgSwallower:

#     def __init__(self, func):
#         self.func = func

#     def __call__(self, *args, **kwargs):
#         self.func()

# def button(callback: Callable, **kwargs):
#     b = ipw.Button(**{**BUTTON_LAYOUT, **kwargs})
#     b.on_click(ArgSwallower(callback))
#     return b

# def toggle_button(callback: Callable, **kwargs):
#     tb = ipw.ToggleButton(**{**BUTTON_LAYOUT, **kwargs})
#     tb.observe(ArgSwallower(callback), names='value')
#     return tb

# def _reset_togglebuttons(owner, *ignored):
#     """
#     If the currently selected value is clicked again, we reset the value to None.
#     """
#     if owner.value == self.current_cut_surface_value:
#         self.cut_surface_buttons.value = None
#     self.current_cut_surface_value = owner.value

# def multi_toggle_button(callback: Callable, **kwargs):
#     tb = ipw.ToggleButtons(**{**BUTTON_LAYOUT, **kwargs})
#     tb.observe(ArgSwallower(callback), names='value')

#     def

#     self.cut_surface_buttons.on_msg(self._check_if_reset_needed)
#     return tb


class ButtonTool(ipw.Button):

    def __init__(self, callback: Callable = None, **kwargs):
        """
        Create a new button with a callback that is called when the button is clicked.
        """
        super().__init__(**{**BUTTON_LAYOUT, **kwargs})
        self._callback = callback
        self.on_click(self)

    def __call__(self, *args, **kwargs):
        self._callback()


class ToggleTool(ipw.ToggleButton):

    def __init__(self, callback: Callable, **kwargs):
        """
        Create a toggle button with a callback that is called when the button is
        toggled. We use a Button and handle the styling ourselves because in some
        cases, we need to toggle the button color without triggering the callback
        function.
        """
        super().__init__(**{**BUTTON_LAYOUT, **kwargs})
        self._callback = callback
        self.observe(self)

    def __call__(self, *args, **kwargs):
        self._callback()


class MultiToggleTool(ipw.ToggleButtons):

    def __init__(self, callback: Callable, **kwargs):
        """
        Create a toggle button with a callback that is called when the button is
        toggled. We use a Button and handle the styling ourselves because in some
        cases, we need to toggle the button color without triggering the callback
        function.
        """
        super().__init__(**{**BUTTON_LAYOUT, **kwargs})
        self._callback = callback
        self.observe(self)

    def __call__(self, *args, **kwargs):
        self._callback()

    # @property
    # def value(self):
    #     return self._value

    # @value.setter
    # def value(self, val):
    #     self._value = val
    #     self._update_color()

    # def _update_color(self):
    #     self.widget.button_style = 'info' if self._value else ''

    # def _toggle(self):
    #     self._value = not self._value
    #     self._update_color()


class PointsTool(ToggleTool):

    def __init__(self, value=False, ax=None, **kwargs):
        from mpltoolbox import Points
        self.points = Points(ax=ax, autostart=False, mec='w')
        super().__init__(callback=self.start_stop,
                         value=value,
                         icon='crosshairs',
                         **kwargs)

    def start_stop(self):
        if self.value:
            self.points.start()
        else:
            self.points.stop()


class ColorTool(ipw.HBox):

    def __init__(self, text, color):
        layout = ipw.Layout(display="flex", justify_content="flex-end", width='150px')
        self.text = ipw.Label(value=text, layout=layout)
        self.color = ipw.ColorPicker(concise=True,
                                     value=color,
                                     description='',
                                     layout={'width': "30px"})
        self.button = ipw.Button(icon='times', **BUTTON_LAYOUT)
        super().__init__([self.text, self.color, self.button])
