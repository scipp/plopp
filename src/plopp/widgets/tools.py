# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .common import BUTTON_LAYOUT, is_sphinx_build

import ipywidgets as ipw
from functools import partial
from typing import Callable


class ButtonTool(ipw.Button):

    def __init__(self, callback: Callable = None, **kwargs):
        """
        Create a button with a callback that is called when the button is clicked.
        """
        super().__init__(**{**BUTTON_LAYOUT, **kwargs})
        self.callback = callback
        self.on_click(self)

    def __call__(self, *ignored):
        self.callback()


class ToggleTool(ipw.ToggleButton):

    def __init__(self, callback: Callable, **kwargs):
        """
        Create a toggle button with a callback that is called when the button is
        toggled.
        """
        super().__init__(**{**BUTTON_LAYOUT, **kwargs})
        self.callback = callback
        self.observe(self, names='value')

    def __call__(self, *ignored):
        self.callback()


class MultiToggleTool(ipw.ToggleButtons):

    def __init__(self, callback: Callable, **kwargs):
        """
        Create toggle buttons with a callback that is called when one of the buttons is
        toggled. In addition to ipywidgets ToggleButtons, when you click the button
        which is already selected, it resets the value to `None` (no button selected).
        """
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

    def reset(self, owner, *ignored):
        """
        If the currently selected button is clicked again, reset value to None.
        """
        if owner.value == self._current_value:
            self.value = None
        self._current_value = owner.value


HomeTool = partial(ButtonTool, icon='home', tooltip='Autoscale view')

LogxTool = partial(ToggleTool, description='logx', tooltip='Toggle X axis scale')

LogyTool = partial(ToggleTool, description='logy', tooltip='Toggle Y axis scale')

LogNormTool = partial(ToggleTool,
                      description='log',
                      tooltip='Toggle colorscale normalization')

SaveTool = partial(ButtonTool, icon='save', tooltip='Save figure')

CameraTool = partial(ButtonTool, icon='camera', tooltip='Autoscale view')

OutlineTool = partial(ToggleTool,
                      value=True,
                      icon='codepen',
                      tooltip='Toggle outline visibility')

AxesTool = partial(ToggleTool,
                   value=True,
                   description='\u27C0',
                   style={'font_weight': 'bold'},
                   tooltip='Toggle visibility of XYZ axes')


class PanZoomTool(MultiToggleTool):

    def __init__(self, canvas, value=None, **kwargs):
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
