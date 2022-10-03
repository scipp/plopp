# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .styling import BUTTON_LAYOUT

import ipywidgets as ipw
from typing import Callable
import numpy as np


class Cut3dTool(ipw.HBox):

    def __init__(self,
                 limits,
                 direction,
                 value: bool = False,
                 color='red',
                 linewidth=1.5,
                 on_activate=None,
                 on_deactivate=None,
                 on_move=None,
                 **kwargs):
        """
        """
        import pythreejs as p3
        self._limits = limits
        self._direction = direction
        w_axis = 2 if self._direction == 'x' else 0
        h_axis = 2 if self._direction == 'y' else 1
        width = limits[w_axis * 2 + 1] - limits[w_axis * 2]
        height = limits[h_axis * 2 + 1] - limits[h_axis * 2]

        self.outline = p3.LineSegments(
            geometry=p3.EdgesGeometry(p3.PlaneBufferGeometry(width=width,
                                                             height=height)),
            material=p3.LineBasicMaterial(color=color, linewidth=linewidth))
        if self._direction == 'x':
            self.outline.rotateY(0.5 * np.pi)
        if self._direction == 'y':
            self.outline.rotateX(0.5 * np.pi)

        self.outline.visible = value

        self.button = ipw.ToggleButton(value=value, **{**BUTTON_LAYOUT, **kwargs})
        axis = 'xyz'.index(self._direction)
        self.slider = ipw.FloatSlider(min=limits[axis * 2],
                                      max=limits[axis * 2 + 1],
                                      layout={'width': '200px'},
                                      disabled=not value)
        self.slider.step = (self.slider.max - self.slider.min) / 100
        self.button.observe(self.toggle, names='value')
        self.slider.observe(self.move, names='value')

        self._on_activate = on_activate
        self._on_deactivate = on_deactivate
        self._on_move = on_move

        super().__init__([self.button, self.slider])

    def toggle(self, change):
        self.outline.visible = change['new']
        self.slider.disabled = not change['new']

    def move(self, value):
        pos = list(self.outline.position)
        axis = 'xyz'.index(self._direction)
        pos[axis] = value['new']
        self.outline.position = pos
