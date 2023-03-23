# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from typing import Any, Callable, Dict, List, Union

import ipywidgets as ipw
import scipp as sc

from ..core import input_node, node, widget_node
from ..core.utils import coord_element_to_string
from .box import VBar


class SliceWidget(VBar):
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

    def __init__(self, sizes: Dict[str, int], coords: Dict[str, sc.Variable]):
        self._slider_dims = list(sizes.keys())
        self.controls = {}
        self.view = None
        children = []

        for dim in self._slider_dims:
            coord = coords[dim]
            slider = ipw.IntSlider(
                step=1,
                description=dim,
                min=0,
                max=sizes[dim] - 1,
                continuous_update=True,
                readout=False,
                layout={"width": "200px"},
                style={'description_width': 'initial'},
            )
            continuous_update = ipw.Checkbox(
                value=True,
                tooltip="Continuous update",
                indent=False,
                layout={"width": "20px"},
            )
            label = ipw.Label(value=coord_element_to_string(coord[dim, 0]))
            ipw.jslink((continuous_update, 'value'),
                       (slider, 'continuous_update'))

            self.controls[dim] = {
                'continuous': continuous_update,
                'slider': slider,
                'label': label,
                'coord': coord,
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
        return {
            dim: self.controls[dim]['slider'].value
            for dim in self._slider_dims
        }


@node
def slice_dims(data_array: sc.DataArray, slices: Dict[str,
                                                      slice]) -> sc.DataArray:
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


def dimslicer(ds: Union[sc.DataArray, sc.Dataset], keep: List[str] = None):
    """
    Create a widget that slices out dimensions from the input data using interactive
    sliders (one for each dimension to slice) and returns the result.

    Parameters
    ----------
    ds:
        The input data.
    keep:
        The dimensions to be kept, all remaining dimensions will be sliced. This should
        be a list of dims. If no dims are provided, the last dim will be kept in the
        case of a 2-dimensional input, while the last two dims will be kept in the case
        of higher dimensional inputs.
    """

    if isinstance(ds, sc.DataArray):
        ds = sc.Dataset({ds.name: ds})

    if keep is None:
        keep = ds.dims[-(2 if ds.ndim > 2 else 1):]

    if isinstance(keep, str):
        keep = [keep]

    if len(keep) == 0:
        raise ValueError(
            'Slicer: the list of dims to be kept cannot be empty.')
    if not all(dim in ds.dims for dim in keep):
        raise ValueError(
            f"Slicer: one or more of the requested dims to be kept {keep} "
            f"were not found in the input's dimensions {ds.dims}.")

    slider = SliceWidget(
        sizes={dim: size
               for dim, size in ds.sizes.items() if dim not in keep},
        coords=ds.meta,
    )
    slider.keep = keep
    slider.slider_node = widget_node(slider)
    slider.data_nodes = [input_node(da) for da in ds.values()]
    slider.output_nodes = [
        slice_dims(data_node, slider.slider_node)
        for data_node in slider.data_nodes
    ]
    return slider
