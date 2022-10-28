# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from scipp import DataArray
from ..core.utils import coord_element_to_string
from ..core import node

import ipywidgets as ipw
from typing import Any, Callable, Dict, List


class SliceWidget(ipw.VBox):
    """
    Widgets containing a slider for each of the requested dimensions.
    The widget uses the input data array to determine the range each slider should have.
    Each slider also comes with a checkbox to toggle on and off the slider's continuous
    update.

    Parameters
    ----------
    data_array:
        The input data array.
    dims:
        The dimensions to make sliders for.
    """

    def __init__(self, data_array: DataArray, dims: List[str]):
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

    def _update_label(self, change: Dict[str, Any]):
        """
        Update the readout label with the coordinate value, instead of the integer
        readout index.
        """
        dim = change['owner'].description
        coord = self.controls[dim]['coord'][dim, change['new']]
        self.controls[dim]['label'].value = coord_element_to_string(coord)

    def _plopp_observe_(self, callback: Callable, **kwargs):
        """
        Special method which is used instead of the ``observe`` method of ``ipywidgets``
        because overriding the ``observe`` method of the ``VBox`` causes issues.
        """
        for dim in self.controls:
            self.controls[dim]['slider'].observe(callback, **kwargs)

    @property
    def value(self) -> Dict[str, int]:
        """
        The widget value, as a dict containing the dims as keys and the slider indices
        as values.
        """
        return {dim: self.controls[dim]['slider'].value for dim in self._slider_dims}


@node
def slice_dims(data_array: DataArray, slices: Dict[str, slice]) -> DataArray:
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
        out = out[dim, sl]
    return out
