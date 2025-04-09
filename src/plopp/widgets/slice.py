# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from functools import partial
from typing import Any

import ipywidgets as ipw
import scipp as sc

from ..core import node
from ..core.utils import coord_element_to_string
from .box import VBar


class _BaseSliceWidget(VBar, ipw.ValueWidget):
    def __init__(self, da: sc.DataArray, dims: list[str], slider_constr: ipw.Widget):
        if isinstance(dims, str):
            dims = [dims]
        self._slider_dims = dims
        self.controls = {}
        self.view = None
        children = []

        for dim in self._slider_dims:
            coord = (
                da.coords[dim]
                if dim in da.coords
                else sc.arange(dim, da.sizes[dim], unit=None)
            )
            widget_args = {
                'step': 1,
                'description': dim,
                'min': 0,
                'max': da.sizes[dim] - 1,
                'value': (da.sizes[dim] - 1) // 2
                if slider_constr is ipw.IntSlider
                else None,
                'continuous_update': True,
                'readout': False,
                'layout': {"width": "200px"},
                'style': {'description_width': 'initial'},
            }
            slider = slider_constr(**widget_args)
            continuous_update = ipw.Checkbox(
                value=True,
                tooltip="Continuous update",
                indent=False,
                layout={"width": "20px"},
            )
            label = ipw.Label(value=coord_element_to_string(coord[dim, slider.value]))
            ipw.jslink((continuous_update, 'value'), (slider, 'continuous_update'))

            self.controls[dim] = {
                'continuous': continuous_update,
                'slider': slider,
                'label': label,
                'coord': coord,
            }
            slider.observe(self._update_label, names='value')
            slider.observe(self._on_subwidget_change, names='value')
            children.append(ipw.HBox([continuous_update, slider, label]))

        self._on_subwidget_change()
        super().__init__(children)

    def _update_label(self, change: dict[str, Any]):
        """
        Update the readout label with the coordinate value, instead of the integer
        readout index.
        """
        dim = change['owner'].description
        coord = self.controls[dim]['coord'][dim, change['new']]
        self.controls[dim]['label'].value = coord_element_to_string(coord)

    def _on_subwidget_change(self, _=None):
        """
        Update the value of the widget.
        The value is a dict containing one entry per slider, giving the slider's value.
        """
        self.value = {
            dim: self.controls[dim]['slider'].value for dim in self._slider_dims
        }


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
