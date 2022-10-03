# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ipywidgets import Button, ToggleButton
from typing import Callable
import numpy as np

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
        self._update_color()

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


class CutTool:

    def __init__(self, limits, direction, value: bool = False, color='black', **kwargs):
        """
        """
        import pythreejs as p3
        self.widget = ToggleButton(value=value, **{**LAYOUT_STYLE, **kwargs})
        self._limits = limits
        self._direction = direction
        w_axis = 2 if self._direction == 'x' else 0
        h_axis = 2 if self._direction == 'y' else 1
        width = (limits[w_axis][1] - limits[w_axis][0]).value
        height = (limits[h_axis][1] - limits[h_axis][0]).value

        self.outline = p3.LineSegments(geometry=p3.EdgesGeometry(
            p3.PlaneBufferGeometry(width=width, height=height)),
                                       material=p3.LineBasicMaterial(color=color))
        if self._direction == 'x':
            self.outline.rotateY(0.5 * np.pi)
        if self._direction == 'y':
            self.outline.rotateX(0.5 * np.pi)

        self.outline.visible = value

        self.widget.observe(self.toggle)

    def toggle(self, change):
        self.outline.visible = change['new']

    def move(self, value):
        pos = list(self.outline.position)
        axis = 'xyz'.index(self._direction)
        pos[axis] = value['new']
        self.outline.position = pos
