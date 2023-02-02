# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from functools import partial
from typing import Callable, List, Optional, Union

import ipywidgets as ipw

from .style import BUTTON_LAYOUT


class ButtonTool(ipw.Button):
    """
    Create a button with a callback that is called when the button is clicked.

    Parameters
    ----------
    callback:
        The function that will be called when the button is clicked.
    **kwargs:
        All other kwargs are forwarded to ipywidgets.Button.
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

    Parameters
    ----------
    callback:
        The function that will be called when the button is toggled.
    **kwargs:
        All other kwargs are forwarded to ipywidgets.ToggleButton.
    """

    def __init__(self, callback: Callable, **kwargs):
        super().__init__(**{**BUTTON_LAYOUT, **kwargs})
        self.callback = callback
        self.observe(self, names='value')

    def __call__(self, *ignored):
        self.callback()


class MultiToggleTool(ipw.VBox):
    """
    Create toggle buttons with a callback that is called when one of the buttons is
    toggled. In addition to ipywidgets ToggleButtons, when you click the button
    which is already selected, it resets the value to `None` (no button selected).

    Parameters
    ----------
    callback:
        The function that will be called when the one of the buttons is toggled.
    options:
        A list of values for the different buttons (one button per value will be
        created).
    icons:
        A list of icons (one icon per button).
    tooltips:
        A list of tooltips (one tooltip per button).
    descriptions:
        A list of descriptions (one description per button).
    value:
        If given, the value of the button with the corresponding option will be set to
        True.
    **kwargs:
        All other kwargs are forwarded to ipywidgets.ToggleButton.
    """

    def __init__(self,
                 callback: Callable,
                 options: List[str],
                 icons: Optional[List[str]] = None,
                 tooltips: List[str] = None,
                 descriptions: List[str] = None,
                 value: Optional[str] = None,
                 **kwargs):

        self.callback = callback
        self._options = options
        self._buttons = {}
        for i, key in enumerate(self._options):
            tb = ipw.ToggleButton(
                icon=icons[i] if icons is not None else None,
                tooltip=tooltips[i] if tooltips is not None else None,
                description=descriptions[i] if descriptions is not None else '',
                value=key == value,
                **{
                    **BUTTON_LAYOUT,
                    **kwargs
                })
            tb._option = key
            tb.observe(self, names='value')
            self._buttons[key] = tb
        self._lock = False
        super().__init__(list(self._buttons.values()))

    def __call__(self, change: dict):
        if self._lock:
            return
        key = change['owner']._option
        self._lock = True
        for name in set(self._buttons.keys()) - {key}:
            if self._buttons[name].value:
                self._buttons[name].value = False
        self._lock = False
        self.callback()

    @property
    def value(self) -> Union[str, None]:
        for b in self._buttons.values():
            if b.value:
                return b._option


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
"""Toggle outline visibility tool"""

AxesTool = partial(ToggleTool,
                   value=True,
                   description='\u27C0',
                   style={'font_weight': 'bold'},
                   tooltip='Toggle visibility of XYZ axes')
"""Toggle RGB axes helper visibility tool"""


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

    def __init__(self, callback: Callable, value: bool = None, **kwargs):
        self._callback = callback
        super().__init__(callback=self._panzoom,
                         options=['pan', 'zoom'],
                         icons=['arrows', 'search-plus'],
                         tooltips=['Pan', 'Zoom'],
                         value=value,
                         **kwargs)

    def _panzoom(self):
        self._callback(self.value)


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
