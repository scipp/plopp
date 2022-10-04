# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from scipp import DataArray
from ..core.utils import coord_element_to_string
from ..core import node

import ipywidgets as ipw
from typing import Callable


class SliceWidget(ipw.VBox):
    """
    Widgets containing a slider for each of the input's dimensions, as well as
    buttons to modify the currently displayed axes.
    """

    def __init__(self, data_array, dims: list):
        self._slider_dims = dims
        self.controls = {}
        self.view = None
        children = []

        for dim in dims:
            coord = data_array.meta[dim]
            slider = ipw.IntSlider(step=1,
                                   description=dim,
                                   min=0,
                                   max=data_array.sizes[dim] - 1,
                                   continuous_update=True,
                                   readout=False,
                                   layout={"width": "200px"},
                                   style={'description_width': 'initial'})
            continuous_update = ipw.Checkbox(value=True,
                                             tooltip="Continuous update",
                                             indent=False,
                                             layout={"width": "20px"})
            label = ipw.Label(value=coord_element_to_string(coord[dim, 0]))
            ipw.jslink((continuous_update, 'value'), (slider, 'continuous_update'))

            self.controls[dim] = {
                'continuous': continuous_update,
                'slider': slider,
                'label': label,
                'coord': coord
            }
            slider.observe(self._update_label, names='value')
            children.append(ipw.HBox([continuous_update, slider, label]))

        super().__init__(children)

    def _update_label(self, change):
        dim = change['owner'].description
        coord = self.controls[dim]['coord'][dim, change['new']]
        self.controls[dim]['label'].value = coord_element_to_string(coord)

    def _plopp_observe_(self, callback: Callable, **kwargs):
        for dim in self.controls:
            self.controls[dim]['slider'].observe(callback, **kwargs)

    @property
    def value(self) -> dict:
        return {dim: self.controls[dim]['slider'].value for dim in self._slider_dims}


@node
def slice_dims(data_array: DataArray, slices: dict) -> DataArray:
    """
    Slice the data according to input slices.
    """
    out = data_array
    for dim, sl in slices.items():
        out = out[dim, sl]
    return out
