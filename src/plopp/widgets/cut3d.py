# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .styling import BUTTON_LAYOUT
from ..core import Node, node

import ipywidgets as ipw
from typing import Callable
import numpy as np
import scipp as sc


class Cut3dTool(ipw.HBox):

    def __init__(
            self,
            *nodes,
            limits,
            direction,
            view,
            # make_points_transparent,
            # maybe_make_points_opaque,
            value: bool = False,
            color='red',
            linewidth=1.5,
            # on_activate=None,
            # on_deactivate=None,
            # on_move=None,
            **kwargs):
        """
        """
        import pythreejs as p3
        self._limits = limits
        self._direction = direction
        axis = 'xyz'.index(self._direction)
        self._dim = self._limits[axis].dim
        self._view = view
        # self._view_children = self._view._children.copy()

        w_axis = 2 if self._direction == 'x' else 0
        h_axis = 2 if self._direction == 'y' else 1
        width = (self._limits[w_axis][1] - self._limits[w_axis][0]).value
        height = (self._limits[h_axis][1] - self._limits[h_axis][0]).value

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
        self.slider = ipw.FloatSlider(min=limits[axis][0].value,
                                      max=limits[axis][1].value,
                                      layout={'width': '200px'},
                                      disabled=not value)
        self.slider.step = (self.slider.max - self.slider.min) / 100
        self.button.observe(self.toggle, names='value')
        self.slider.observe(self.move, names='value')

        self._nodes = nodes[0]
        # print(self._nodes)

        # self._on_activate = on_activate
        # self._on_deactivate = on_deactivate
        # self._on_move = on_move

        super().__init__([self.button, self.slider])

    def toggle(self, change):
        self.outline.visible = change['new']
        self.slider.disabled = not change['new']
        if change['new']:
            self._add_node()
            # self._make_points_transparent()
            # for child in self._view_children.values():
            #     child.opacity = 0.1
        # else:
        # self._maybe_make_points_opaque()

    def move(self, value):
        pos = list(self.outline.position)
        axis = 'xyz'.index(self._direction)
        pos[axis] = value['new']
        self.outline.position = pos

    def _add_node(self):
        self.pos_node = Node(lambda: sc.scalar(self.slider.value, unit='m'))
        self.select_node = node(lambda da, pos: da[sc.abs(da.meta[
            self._dim] - pos) < sc.scalar(10., unit='m')])(da=self._nodes,
                                                           pos=self.pos_node)
        # print(self.select_node.request_data())
        self.select_node.add_view(self._view)
        # print('self._view.graph_nodes', self._view.graph_nodes)
        self._view.update(self.select_node.request_data(),
                          key=self.select_node.id,
                          from_cut=True)

    @property
    def value(self):
        return self.button.value
