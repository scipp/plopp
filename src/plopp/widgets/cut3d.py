# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .styling import BUTTON_LAYOUT
from ..core import Node, node

import ipywidgets as ipw
import numpy as np
import scipp as sc
import asyncio


class Timer:
    """
    From:
    https://ipywidgets.readthedocs.io/en/8.0.2/examples/Widget%20Events.html#Debouncing
    """

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
    """
    Decorator that will postpone a function's
    execution until after `wait` seconds
    have elapsed since the last time it was invoked.

    From:
    https://ipywidgets.readthedocs.io/en/8.0.2/examples/Widget%20Events.html#Debouncing
    """

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

    def __init__(self,
                 *nodes,
                 limits,
                 direction,
                 view,
                 value: bool = False,
                 color='red',
                 linewidth=1.5,
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

        center = [var.mean().value for var in self._limits]
        self.outline.position = center
        self.outline.visible = value

        self.thickness = 0.01
        self._thickness_step = self.thickness * 0.25

        self.button = ipw.ToggleButton(value=value, **{**BUTTON_LAYOUT, **kwargs})
        self.slider = ipw.FloatSlider(min=limits[axis][0].value,
                                      max=limits[axis][1].value,
                                      value=center[axis],
                                      layout={'width': '150px'},
                                      disabled=not value,
                                      readout=False)
        self.slider.step = (self.slider.max - self.slider.min) * self.thickness * 0.5
        self.readout = ipw.FloatText(disabled=not value,
                                     layout={'width': '70px'},
                                     step=self.slider.step)
        self.unit_label = ipw.Label(f'[{self._unit}]')
        ipw.jslink((self.slider, "value"), (self.readout, "value"))

        layout = {'width': '12px', 'padding': '0px'}
        self.button_plus = ipw.Button(icon='plus',
                                      layout=layout,
                                      disabled=not value,
                                      tooltip='Increase cut thickness')
        self.button_minus = ipw.Button(icon='minus',
                                       layout=layout,
                                       disabled=not value,
                                       tooltip='Decrease cut thickness')

        self.button.observe(self.toggle, names='value')
        self.slider.observe(self.move, names='value')
        self.slider.observe(self.update_cut, names='value')
        self.button_plus.on_click(self.increase_thickness)
        self.button_minus.on_click(self.decrease_thickness)

        self._nodes = nodes
        self.select_nodes = {}

        super().__init__([
            self.button, self.button_plus, self.button_minus, self.slider, self.readout,
            self.unit_label
        ])

    def toggle(self, change):
        self.outline.visible = change['new']
        for widget in (self.slider, self.button_plus, self.button_minus, self.readout):
            widget.disabled = not change['new']
        if change['new']:
            self._add_cut()
        else:
            self._remove_cut()

    def move(self, value):
        pos = list(self.outline.position)
        axis = 'xyz'.index(self._direction)
        pos[axis] = value['new']
        self.outline.position = pos
        self._remove_cut()

    def _add_cut(self):
        for n in self._nodes:
            da = n.request_data()
            delta = sc.scalar((self.slider.max - self.slider.min) * self.thickness,
                              unit=self._unit)
            pos = sc.scalar(self.slider.value, unit=self._unit)
            selection = sc.abs(da.meta[self._dim] - pos) < delta
            if selection.sum().value > 0:
                self.select_nodes[n.id] = node(lambda da: da[selection])(da=n)
                self.select_nodes[n.id].add_view(self._view)
                self._view.update(self.select_nodes[n.id].request_data(),
                                  key=self.select_nodes[n.id].id,
                                  colormapper=n.id)

    def _remove_cut(self):
        for n in self.select_nodes.values():
            self._view.remove(n.id)
            n.remove()
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
