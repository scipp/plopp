# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)


from functools import partial
from typing import Any, Literal

import ipywidgets as ipw
import numpy as np
import scipp as sc

from ..core import View, node
from ..utils import deprecated
from .debounce import debounce
from .style import BUTTON_LAYOUT
from .tools import PlusMinusTool


@deprecated("Use ``Clip3dTool`` instead.")
class Cut3dTool(ipw.HBox):
    """
    A tool that provides a slider to extract a plane of points in a three-dimensional
    scatter plot, and add it to the scene as an opaque cut. The slider controls the
    position of the slice. When the slider is dragged, the red outline of the cut is
    moved at the same time, while the actual point cloud gets updated less frequently
    using a debounce mechanism.

    The tool also has two buttons +/- to increase/decrease the thickness of the cut.

    .. deprecated:: v24.04.0

    Parameters
    ----------
    view:
        The 3d figure that contains the point clouds to be cut.
    limits:
        The spatial extent of the points in the 3d figure in the XYZ directions.
    direction:
        The direction normal to the slice.
    value:
        Set the cut to active upon creation if ``True``.
    color:
        Color of the cut's outline.
    linewidth:
        Width of the line delineating the outline.
    **kwargs:
        The kwargs are forwarded to the ToggleButton from ``ipywidgets``.
    """

    def __init__(
        self,
        view: View,
        limits: tuple[sc.Variable, sc.Variable, sc.Variable],
        direction: Literal['x', 'y', 'z'],
        value: bool = False,
        color: str = 'red',
        linewidth: float = 1.5,
        **kwargs,
    ):
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
            geometry=p3.EdgesGeometry(
                p3.PlaneBufferGeometry(width=width, height=height)
            ),
            material=p3.LineBasicMaterial(color=color, linewidth=linewidth),
        )
        if self._direction == 'x':
            self.outline.rotateY(0.5 * np.pi)
        if self._direction == 'y':
            self.outline.rotateX(0.5 * np.pi)

        center = [var.mean().value for var in self._limits]
        self.outline.position = center
        self.outline.visible = value

        self.thickness = 0.01
        self._thickness_step = self.thickness * 0.25

        self.button = ipw.ToggleButton(value=value, **kwargs)
        self.slider = ipw.FloatSlider(
            min=limits[axis][0].value,
            max=limits[axis][1].value,
            value=center[axis],
            layout={'width': '150px', 'padding': '0px'},
            disabled=not value,
            readout=False,
        )
        self.slider.step = (self.slider.max - self.slider.min) * self.thickness * 0.5
        self.readout = ipw.FloatText(
            layout={'width': '70px'}, step=self.slider.step, disabled=not value
        )
        self.unit_label = ipw.Label(f'[{self._unit}]')
        ipw.jslink((self.slider, "value"), (self.readout, "value"))

        self.plus_minus = PlusMinusTool(
            plus={
                'callback': self.increase_thickness,
                'tooltip': 'Increase cut thickness',
                'disabled': not value,
            },
            minus={
                'callback': self.decrease_thickness,
                'tooltip': 'Decrease cut thickness',
                'disabled': not value,
            },
        )

        self.button.observe(self.toggle, names='value')
        self.slider.observe(self.move, names='value')
        self.slider.observe(self.update_cut, names='value')

        self._nodes = list(self._view.graph_nodes.values())
        self.select_nodes = {}

        super().__init__(
            [
                ipw.VBox([self.button, self.plus_minus]),
                ipw.VBox(
                    [self.slider, ipw.HBox([self.readout, self.unit_label])],
                    layout={'align_items': 'center'},
                ),
            ]
        )

    def toggle(self, change: dict[str, Any]):
        """
        Toggle the tool on and off.
        """
        self.outline.visible = change['new']
        for widget in (self.slider, self.plus_minus, self.readout):
            widget.disabled = not change['new']
        if change['new']:
            self._add_cut()
        else:
            self._remove_cut()

    def move(self, value: dict[str, Any]):
        """
        Move the outline of the cut according to new position given by the slider.
        """
        pos = list(self.outline.position)
        axis = 'xyz'.index(self._direction)
        pos[axis] = value['new']
        self.outline.position = pos
        self._remove_cut()

    def _add_cut(self):
        """
        Add a point cloud representing the points that intersect the cut plane.
        """

        def select(da, s):
            return da[s]

        for n in self._nodes:
            da = n.request_data()
            delta = sc.scalar(
                (self.slider.max - self.slider.min) * self.thickness, unit=self._unit
            )
            pos = sc.scalar(self.slider.value, unit=self._unit)
            selection = sc.abs(da.coords[self._dim] - pos) < delta
            if selection.sum().value > 0:
                self.select_nodes[n.id] = node(partial(select, s=selection))(da=n)
                self.select_nodes[n.id].add_view(self._view)
                self._view.update(
                    {self.select_nodes[n.id].id: self.select_nodes[n.id].request_data()}
                )

    def _remove_cut(self):
        """
        Remove a cut point the scene.
        """
        for n in self.select_nodes.values():
            self._view.remove(n.id)
            n.remove()
        self.select_nodes.clear()

    @debounce(0.3)
    def update_cut(self, _):
        """
        Update the position of the point cloud. This uses the debounce mechanism to
        avoid updating the cloud too often, and instead rely on simply moving the
        outline, which is cheap.
        """
        if self.value:
            self._add_cut()

    @property
    def value(self):
        """
        Return the state of the ToggleButton.
        """
        return self.button.value

    def increase_thickness(self):
        """
        Increase the thickness of the cut.
        """
        self.thickness = self.thickness + self._thickness_step
        self._remove_cut()
        self._add_cut()

    def decrease_thickness(self):
        """
        Decrease the thickness of the cut.
        """
        self.thickness = max(self.thickness - self._thickness_step, 0)
        self._remove_cut()
        self._add_cut()


@deprecated("Use ``ClippingPlanes`` instead.")
class TriCutTool(ipw.HBox):
    """
    A collection of :class:`Cut3dTool` to make spatial cuts in the X, Y, and Z
    directions on a three-dimensional scatter plot.

    .. deprecated:: v24.04.0

    Parameters
    ----------
    fig:
        The 3d figure that contains the point clouds to be cut.
    """

    def __init__(self, fig: View):
        self._fig = fig
        limits = self._fig.get_limits()
        self.cut_x = Cut3dTool(
            view=self._fig,
            direction='x',
            limits=limits,
            description='X',
            icon='cube',
            **BUTTON_LAYOUT,
        )
        self.cut_y = Cut3dTool(
            view=self._fig,
            direction='y',
            limits=limits,
            description='Y',
            icon='cube',
            **BUTTON_LAYOUT,
        )
        self.cut_z = Cut3dTool(
            view=self._fig,
            direction='z',
            limits=limits,
            description='Z',
            icon='cube',
            **BUTTON_LAYOUT,
        )

        self._fig.canvas.add(
            [self.cut_x.outline, self.cut_y.outline, self.cut_z.outline]
        )

        self.opacity = ipw.BoundedFloatText(
            min=0,
            max=0.5,
            step=0.01,
            disabled=True,
            value=0.03,
            style={'description_width': 'initial'},
            layout={'width': '50px', 'padding': '0px 0px 0px 0px'},
        )
        self.opacity.observe(self._set_opacity, names='value')

        self.cut_x.button.observe(self._toggle_opacity, names='value')
        self.cut_y.button.observe(self._toggle_opacity, names='value')
        self.cut_z.button.observe(self._toggle_opacity, names='value')

        space = ipw.HBox([], layout={'width': '10px'})
        super().__init__(
            [
                self.cut_x,
                space,
                self.cut_y,
                space,
                self.cut_z,
                space,
                ipw.VBox([ipw.Label('Opacity:'), self.opacity]),
            ]
        )
        self.layout.display = 'none'

    def _toggle_opacity(self, _):
        """
        If any cut is active, set the opacity of the original children (not the cuts) to
        a low value. If all cuts are inactive, set the opacity back to 1.
        """
        active_cut = any([self.cut_x.value, self.cut_y.value, self.cut_z.value])
        self.opacity.disabled = not active_cut
        opacity = self.opacity.value if active_cut else 1.0
        self._set_opacity({'new': opacity})

    def _set_opacity(self, change: dict[str, Any]):
        """
        Set the opacity of the original point clouds in the figure, not the cuts.
        """
        self._fig.set_opacity(change['new'])

    def toggle_visibility(self):
        """
        Toggle the visibility of the control buttons for making the cuts.
        """
        self.layout.display = None if self.layout.display == 'none' else 'none'
