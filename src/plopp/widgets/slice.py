# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from functools import partial
from typing import Any

import ipywidgets as ipw
import scipp as sc

from ..core import node
from ..core.utils import coord_element_to_string
from .box import VBar


class DimSlicer(ipw.VBox):
    def __init__(
        self,
        dim: str,
        size: int,
        coord: sc.Variable,
        slider_constr: type[ipw.Widget],
        enable_player: bool = False,
    ):
        if enable_player and not issubclass(slider_constr, ipw.IntSlider):
            raise TypeError(
                "Player can only be enabled for IntSlider, not for IntRangeSlider."
            )
        widget_args = {
            'step': 1,
            'description': dim,
            'min': 0,
            'max': size - 1,
            'value': (size - 1) // 2 if slider_constr is ipw.IntSlider else None,
            'continuous_update': True,
            'readout': False,
            'layout': {"width": "200px", "margin": "0px 0px 0px 10px"},
            'style': {'description_width': 'initial'},
        }
        self.slider = slider_constr(**widget_args)
        self.continuous_update = ipw.Checkbox(
            value=True,
            tooltip="Continuous update",
            indent=False,
            layout={"width": "20px"},
        )
        self.label = ipw.Label(
            value=coord_element_to_string(coord[dim, self.slider.value])
        )
        ipw.jslink(
            (self.continuous_update, 'value'), (self.slider, 'continuous_update')
        )

        children = [self.slider, self.continuous_update, self.label]
        if enable_player:
            self.player = ipw.Play(
                value=self.slider.value,
                min=self.slider.min,
                max=self.slider.max,
                step=self.slider.step,
                interval=100,
                description='Play',
            )
            ipw.jslink((self.player, 'value'), (self.slider, 'value'))
            children.insert(0, self.player)

        self.dim = dim
        self.coord = coord
        self.slider.observe(self._update_label, names='value')

        super().__init__([ipw.HBox(children)])

    def _update_label(self, change: dict[str, Any]):
        """
        Update the readout label with the coordinate value, instead of the integer
        readout index.
        """
        self.label.value = coord_element_to_string(self.coord[self.dim, change['new']])

    @property
    def value(self) -> int | tuple[int, int]:
        """
        The value of the slider.
        """
        return self.slider.value

    @value.setter
    def value(self, value: int | tuple[int, int]):
        self.slider.value = value


class _BaseSliceWidget(VBar, ipw.ValueWidget):
    def __init__(
        self,
        da: sc.DataArray,
        dims: list[str],
        slider_constr: ipw.Widget,
        enable_player: bool = False,
    ):
        if isinstance(dims, str):
            dims = [dims]
        self.controls = {}
        self.view = None
        children = []

        for dim in dims:
            coord = (
                da.coords[dim]
                if dim in da.coords
                else sc.arange(dim, da.sizes[dim], unit=None)
            )
            self.controls[dim] = DimSlicer(
                dim=dim,
                size=da.sizes[dim],
                coord=coord,
                slider_constr=slider_constr,
                enable_player=enable_player,
            )
            self.controls[dim].slider.observe(self._on_subwidget_change, names='value')
            children.append(self.controls[dim])

        self._on_subwidget_change()
        super().__init__(children)

    def _on_subwidget_change(self, _=None):
        """
        Update the value of the widget.
        The value is a dict containing one entry per slider, giving the slider's value.
        """
        self.value = {dim: slicer.slider.value for dim, slicer in self.controls.items()}


SliceWidget = partial(_BaseSliceWidget, slider_constr=ipw.IntSlider)
"""
Widgets containing a slider for each of the requested dimensions.
The widget uses the input data array to determine the range each slider should have.
Each slider also comes with a checkbox to toggle on and off the slider's continuous
update.

Parameters
----------
da:
    The input data array.
dims:
    The dimensions to make sliders for.
enable_player:
    Add a play button to animate the slider if True. Defaults to False.

    .. versionadded:: 25.07.0
"""

RangeSliceWidget = partial(_BaseSliceWidget, slider_constr=ipw.IntRangeSlider)
"""
Widgets containing a slider for each of the requested dimensions.
The widget uses the input data array to determine the range each slider should have.
Each slider also comes with a checkbox to toggle on and off the slider's continuous
update.

.. versionadded:: 24.04.0

Parameters
----------
da:
    The input data array.
dims:
    The dimensions to make sliders for.
"""


@node
def slice_dims(data_array: sc.DataArray, slices: dict[str, slice]) -> sc.DataArray:
    """
    Slice the data according to input slices.

    Parameters
    ----------
    data_array:
        The input data array to be sliced.
    slices:
        Dict of slices to apply for each dimension.
    """
    out = data_array
    for dim, sl in slices.items():
        if isinstance(sl, tuple):
            sl = slice(*sl)
        out = out[dim, sl]
    return out
