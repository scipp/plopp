# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ipywidgets import Button, VBox
from typing import Callable
import ipywidgets as ipw

LAYOUT_STYLE = {"layout": {"width": "34px", "padding": "0px 0px 0px 0px"}}


class ButtonTool:

    def __init__(self, callback: Callable = None, **kwargs):
        """
        Create a new button with a callback that is called when the button is clicked.
        """
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
        self.widget = Button(**{**LAYOUT_STYLE, **kwargs})
        self._callback = callback
        self.widget.on_click(self)
        self._value = value

    def __call__(self, *args, **kwargs):
        self._toggle()
        self._callback(self.value)

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


class PointsTool(ToggleTool):

    def __init__(self, value=False, ax=None, **kwargs):
        from mpltoolbox import Points
        self.points = Points(ax=ax, autostart=False)
        super().__init__(callback=self.start_stop,
                         value=value,
                         icon='line-chart',
                         **kwargs)

    def start_stop(self, value):
        if value:
            self.points.start()
        else:
            self.points.stop()
