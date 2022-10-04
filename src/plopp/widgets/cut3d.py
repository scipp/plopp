# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .styling import BUTTON_LAYOUT
from ..core import Node, node

from itertools import chain
import ipywidgets as ipw
from typing import Callable
import numpy as np
import scipp as sc

import asyncio


class Timer:

    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback

    async def _job(self):
        await asyncio.sleep(self._timeout)
        self._callback()

    def start(self):
        self._task = asyncio.ensure_future(self._job())

    def cancel(self):
        self._task.cancel()


def debounce(wait):
    """ Decorator that will postpone a function's
        execution until after `wait` seconds
        have elapsed since the last time it was invoked. """

    def decorator(fn):
        timer = None

        def debounced(*args, **kwargs):
            nonlocal timer

            def call_it():
                fn(*args, **kwargs)

            if timer is not None:
                timer.cancel()
            timer = Timer(wait, call_it)
            timer.start()

        return debounced

    return decorator


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
        self._unit = self._limits[axis].unit
        self._view = view

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

        self.thickness = 0.01
        self._thickness_step = self.thickness * 0.25

        self.button = ipw.ToggleButton(value=value, **{**BUTTON_LAYOUT, **kwargs})
        self.slider = ipw.FloatSlider(min=limits[axis][0].value,
                                      max=limits[axis][1].value,
                                      layout={'width': '200px'},
                                      disabled=not value)
        self.slider.step = (self.slider.max - self.slider.min) * self.thickness * 0.5

        layout = {'width': '20px', 'height': '12px', 'padding': '0px'}
        self.button_plus = ipw.Button(description='\u1429', layout=layout)
        self.button_plus.style.font_size = '38px'
        self.button_minus = ipw.Button(description='\u039e', layout=layout)
        self.button_minus.style.font_size = '25px'

        self.button.observe(self.toggle, names='value')
        self.slider.observe(self.move, names='value')
        self.slider.observe(self.update_cut, names='value')
        self.button_plus.on_click(self.increase_thickness)
        self.button_minus.on_click(self.decrease_thickness)

        self._nodes = nodes
        self.pos_nodes = {}
        self.select_nodes = {}
        # print(self._nodes)

        # self._on_activate = on_activate
        # self._on_deactivate = on_deactivate
        # self._on_move = on_move

        super().__init__(
            [self.button,
             ipw.VBox([self.button_plus, self.button_minus]), self.slider])

    def toggle(self, change):
        self.outline.visible = change['new']
        self.slider.disabled = not change['new']
        if change['new']:
            self._add_cut()
        else:
            self._remove_cut()
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
        self._remove_cut()

    def _add_cut(self):
        for n in self._nodes:
            self.pos_nodes[n.id] = Node(
                lambda: sc.scalar(self.slider.value, unit=self._unit))
            delta = (self.slider.max - self.slider.min) * self.thickness
            self.select_nodes[n.id] = node(lambda da, pos: da[sc.abs(da.meta[
                self._dim] - pos) < sc.scalar(delta, unit=self._unit)])(
                    da=n, pos=self.pos_nodes[n.id])
            # print(self.select_node.request_data())
            self.select_nodes[n.id].add_view(self._view)
            # print('self._view.graph_nodes', self._view.graph_nodes)
            self._view.update(self.select_nodes[n.id].request_data(),
                              key=self.select_nodes[n.id].id,
                              colormapper=n.id)

    def _remove_cut(self):
        for key in self.pos_nodes:
            self._view.remove(self.select_nodes[key].id)
            self.select_nodes[key].remove()
            self.pos_nodes[key].remove()
        self.pos_nodes.clear()
        self.select_nodes.clear()

    @debounce(0.3)
    def update_cut(self, change):
        if self.value:
            self._add_cut()

    @property
    def value(self):
        return self.button.value

    def increase_thickness(self, change):
        self.thickness = self.thickness + self._thickness_step
        self._remove_cut()
        self._add_cut()

    def decrease_thickness(self, change):
        self.thickness = max(self.thickness - self._thickness_step, 0)
        self._remove_cut()
        self._add_cut()
