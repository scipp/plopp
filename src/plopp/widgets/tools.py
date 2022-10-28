# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .common import BUTTON_LAYOUT, is_sphinx_build
from ..graphics import Canvas

import ipywidgets as ipw
from functools import partial
from typing import Callable
from matplotlib.pyplot import Axes


class ButtonTool(ipw.Button):
    """
    Create a button with a callback that is called when the button is clicked.
    """

    def __init__(self, callback: Callable = None, **kwargs):
        super().__init__(**{**BUTTON_LAYOUT, **kwargs})
        self.callback = callback
        self.on_click(self)

    def __call__(self, *ignored):
        self.callback()


class ToggleTool(ipw.ToggleButton):
    """
    Create a toggle button with a callback that is called when the button is
    toggled.
    """

    def __init__(self, callback: Callable, **kwargs):
        super().__init__(**{**BUTTON_LAYOUT, **kwargs})
        self.callback = callback
        self.observe(self, names='value')

    def __call__(self, *ignored):
        self.callback()


class MultiToggleTool(ipw.ToggleButtons):
    """
    Create toggle buttons with a callback that is called when one of the buttons is
    toggled. In addition to ipywidgets ToggleButtons, when you click the button
    which is already selected, it resets the value to `None` (no button selected).
    """

    def __init__(self, callback: Callable, **kwargs):
        args = {
            'layout': {
                "width": "40px",
                "padding": "0px 0px 0px 0px"
            },
            'style': {
                'button_width':
                # See https://github.com/jupyter-widgets/ipywidgets/issues/2517
                BUTTON_LAYOUT['layout']['width'] if is_sphinx_build() else '17px',
                'description_width':
                '0px'
            }
        }
        super().__init__(**{**args, **kwargs})
        self.callback = callback
        self._current_value = self.value
        self.observe(self, names='value')
        self.on_msg(self.reset)

    def __call__(self, *ignored):
        self.callback()

    def reset(self, owner: ipw.Widget, *ignored):
        """
        If the currently selected button is clicked again, reset value to None.
        """
        if owner.value == self._current_value:
            self.value = None
        self._current_value = owner.value


HomeTool = partial(ButtonTool, icon='home', tooltip='Autoscale view')
"""Return home tool."""

LogxTool = partial(ToggleTool, description='logx', tooltip='Toggle X axis scale')
"""Toggle horizontal axis scale tool."""

LogyTool = partial(ToggleTool, description='logy', tooltip='Toggle Y axis scale')
"""Toggle vertical axis scale tool."""

LogNormTool = partial(ToggleTool,
                      description='log',
                      tooltip='Toggle colorscale normalization')
"""Toggle normalization scale tool."""

SaveTool = partial(ButtonTool, icon='save', tooltip='Save figure')
"""Save figure to png tool."""

CameraTool = partial(ButtonTool, icon='camera', tooltip='Autoscale view')
"""Tool for changing the position of the camera in a 3d scene."""

OutlineTool = partial(ToggleTool,
                      value=True,
                      icon='codepen',
                      tooltip='Toggle outline visibility')
"""Toggle outline visbility tool"""

AxesTool = partial(ToggleTool,
                   value=True,
                   description='\u27C0',
                   style={'font_weight': 'bold'},
                   tooltip='Toggle visibility of XYZ axes')
"""Toggle RGB axes helper visbility tool"""


class PanZoomTool(MultiToggleTool):
    """
    Tool to control the panning and zooming actions on a Matplotlib figure.

    Parameters
    ----------
    canvas:
        The canvas to act upon.
    value:
        Set the initially selected button. No button selected if ``None``.
    """

    def __init__(self, canvas: Canvas, value: bool = None, **kwargs):
        self._canvas = canvas
        super().__init__(callback=self._pan_zoom,
                         options=[('', 'pan'), (' ', 'zoom')],
                         icons=['arrows', 'search-plus'],
                         tooltips=['Pan', 'Zoom'],
                         value=value,
                         **kwargs)

    def _pan_zoom(self):
        if self.value == 'zoom':
            self._canvas.zoom()
        elif self.value == 'pan':
            self._canvas.pan()
        elif self.value is None:
            self._canvas.reset_mode()


class PointsTool(ToggleTool):
    """
    Tool to add point markers onto a figure.

    Parameters
    ----------
    value:
        Set the toggle button value on creation.
    ax:
        The Matplotlib axes where the points will be drawn.
    """

    def __init__(self, value: bool = False, ax: Axes = None, **kwargs):
        from mpltoolbox import Points
        self.points = Points(ax=ax, autostart=False, mec='w')
        super().__init__(callback=self.start_stop,
                         value=value,
                         icon='crosshairs',
                         **kwargs)

    def start_stop(self):
        """
        Toggle start or stop of the tool.
        """
        if self.value:
            self.points.start()
        else:
            self.points.stop()


class ColorTool(ipw.HBox):
    """
    Tool for saving lines and controlling their color.
    It also comes with a close button to remove a line.

    Parameters
    ----------
    text:
        Text label for the tool.
    color:
        Initial color.
    """

    def __init__(self, text: str, color: str):
        layout = ipw.Layout(display="flex", justify_content="flex-end", width='150px')
        self.text = ipw.Label(value=text, layout=layout)
        self.color = ipw.ColorPicker(concise=True,
                                     value=color,
                                     description='',
                                     layout={'width': "30px"})
        self.button = ipw.Button(icon='times', **BUTTON_LAYOUT)
        super().__init__([self.text, self.color, self.button])
