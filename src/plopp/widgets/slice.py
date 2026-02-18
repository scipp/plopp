# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from functools import partial
from typing import Any

import ipywidgets as ipw
import scipp as sc

from ..core import node
from ..core.utils import coord_element_to_string
from .box import VBar


class DimSlicer(ipw.HBox):
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
            'min': 0,
            'max': size - 1,
            'value': (size - 1) // 2 if slider_constr is ipw.IntSlider else None,
            'continuous_update': True,
            'readout': False,
            'layout': {"width": "15.2em", "margin": "0px 0px 0px 10px"},
        }
        self._is_bin_edges = coord.sizes[dim] > size
        self.dim_label = ipw.Label(value=dim)
        self.slider = slider_constr(**widget_args)
        self.continuous_update = ipw.Checkbox(
            value=True,
            tooltip="Continuous update",
            indent=False,
            layout={"width": "1.52em"},
        )
        self.label = ipw.Label()
        ipw.jslink(
            (self.continuous_update, 'value'), (self.slider, 'continuous_update')
        )

        children = [self.dim_label, self.slider, self.continuous_update, self.label]
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
        self._update_label({"new": self.slider.value})
        self.slider.observe(self._update_label, names='value')

        super().__init__(children)

    def _update_label(self, change: dict[str, Any]):
        """
        Update the readout label with the coordinate value, instead of the integer
        readout index.
        """
        inds = change["new"]
        if self._is_bin_edges:
            if isinstance(inds, tuple):
                inds = (inds[0], inds[1] + 1)
            else:
                inds = (inds, inds + 1)
        self.label.value = coord_element_to_string(self.coord[self.dim, inds])

    @property
    def value(self) -> int | tuple[int, int]:
        """
        The value of the slider.
        """
        return self.slider.value

    @value.setter
    def value(self, value: int | tuple[int, int]):
        self.slider.value = value


class CombinedSlicer(ipw.HBox):
    def __init__(
        self,
        dim: str,
        size: int,
        coord: sc.Variable,
        width: str = "25em",
        **ignored,
    ):

        self.int_slicer = DimSlicer(
            dim=dim, size=size, coord=coord, slider_constr=ipw.IntSlider
        )
        self.int_slicer.slider.value = self.int_slicer.slider.min
        self.int_slicer.slider.layout = {"width": width}

        self.range_slicer = DimSlicer(
            dim=dim, size=size, coord=coord, slider_constr=ipw.IntRangeSlider
        )
        self.range_slicer.slider.value = 0, size
        self.range_slicer.slider.layout = {"width": width}

        self.int_slicer.slider.observe(self.move_range, names='value')

        self.slider_toggler = ipw.ToggleButtons(
            options=["o-o", "-o-"],
            tooltips=['Range slider', 'Single handle slider'],
            style={"button_width": "3.2em"},
        )

        self.slider_toggler.observe(self.toggle_slider_mode, names='value')

        # children = [self.slider_toggler, self.range_slicer]

        super().__init__([self.slider_toggler, self.range_slicer])

    def move_range(self, change):
        self.range_slicer.slider.value = (change["new"], change["new"])

    def toggle_slider_mode(self, change):
        if change["new"] == "o-o":
            self.children = [self.slider_toggler, self.range_slicer]
        else:
            self.int_slicer.slider.value = int(
                0.5 * sum(self.range_slicer.slider.value)
            )
            self.children = [self.slider_toggler, self.int_slicer]

    @property
    def slider(self) -> ipw.Widget:
        return self.range_slicer.slider

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
        slicer_constr: type[DimSlicer] | type[CombinedSlicer],
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
            self.controls[dim] = slicer_constr(
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
        self.value = {dim: slicer.value for dim, slicer in self.controls.items()}


SliceWidget = partial(
    _BaseSliceWidget, slider_constr=ipw.IntSlider, slicer_constr=DimSlicer
)
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

RangeSliceWidget = partial(
    _BaseSliceWidget, slider_constr=ipw.IntRangeSlider, slicer_constr=DimSlicer
)
"""
Widgets containing a range slider for each of the requested dimensions.
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

CombinedSliceWidget = partial(
    _BaseSliceWidget, slider_constr=None, slicer_constr=CombinedSlicer
)
"""
Widgets containing a combined slider (able to toggle between normal slider and range
slider) for each of the requested dimensions.
The widget uses the input data array to determine the range each slider should have.
Each slider also comes with a checkbox to toggle on and off the slider's continuous
update.

.. versionadded:: 26.03.0

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
            # Include the stop index in the slice, as we expect both slider handles to
            # be inclusive.
            sl = slice(sl[0], sl[1] + 1)
        out = out[dim, sl]
    return out
