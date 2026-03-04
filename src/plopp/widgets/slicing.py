# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from functools import partial

import ipywidgets as ipw
import numpy as np
import scipp as sc
from traitlets import Any

from ..core import node
from .box import VBar


def _find_closest_index(coord, value: str) -> int:
    try:
        v = float(value)
    except ValueError:
        v = sc.datetime(value).to(unit="ns").value.astype(int)
    return np.argmin(np.abs(coord - v))


class BoundedText(ipw.HBox, ipw.ValueWidget):
    value = Any().tag(sync=True)

    def __init__(
        self,
        coord: sc.Variable,
        index: int,
        continuous_update: bool = False,
        layout=None,
        **kwargs,
    ):
        self._lock = False
        self._coord = coord.values
        if self._coord.dtype not in (sc.DType.datetime64, sc.DType.string):
            self._underlying = self._coord
            self._fmt = ".3E"
            if layout is None:
                layout = {"width": "11.5ch"}
        else:
            if self._coord.dtype == sc.DType.datetime64:
                self._underlying = coord.to(unit="ns").values.astype(int)
            else:
                self._underlying = self._coord
            self._fmt = ""
            if layout is None:
                layout = {"width": f"{len(str(self._coord[-1])) * 1.02}ch"}

        self._widget = ipw.Text(
            continuous_update=continuous_update, value="", layout=layout, **kwargs
        )
        self.min = 0
        self.max = len(self._coord)
        # observe user edits
        self._widget.observe(self._on_child_change, names="value")
        # observe external value changes
        self.observe(self._on_value_change, names="value")

        super().__init__([self._widget])
        self.value = index

    def _on_child_change(self, change):
        if self._lock:
            return

        new = _find_closest_index(coord=self._underlying, value=change["new"])
        new = min(max(new, self.min), self.max)
        self._lock = True
        self._widget.value = f"{self._coord[new]:{self._fmt}}"
        self.value = new
        self._lock = False

    def _on_value_change(self, change):
        if self._lock:
            return

        new = min(max(change["new"], self.min), self.max)
        self._lock = True
        self._widget.value = f"{self._coord[new]:{self._fmt}}"
        self._lock = False


class BoundedBinEdgeText(ipw.HBox, ipw.ValueWidget):
    value = Any().tag(sync=True)

    def __init__(
        self,
        coord: sc.Variable,
        index: int,
        continuous_update: bool = False,
        layout=None,
        **kwargs,
    ):
        self._lock = False
        self._coord = coord.values
        if self._coord.dtype not in (sc.DType.datetime64, sc.DType.string):
            self._fmt = ".3E"
            if layout is None:
                layout = {"width": "22.5ch"}
        else:
            self._fmt = ""
            if layout is None:
                layout = {"width": f"{0.92 * (len(str(self._coord[-1])) * 2 + 3)}ch"}

        self._widget = ipw.Text(
            continuous_update=continuous_update, value="", layout=layout, **kwargs
        )
        self.min = 0
        self.max = len(self._coord) - 1
        # observe user edits
        self._widget.observe(self._on_child_change, names="value")
        # observe external value changes
        self.observe(self._on_value_change, names="value")

        super().__init__([self._widget])
        self.value = index, index + 1

    def _on_child_change(self, change):
        if self._lock:
            return

        new = [
            _find_closest_index(coord=self._coord, value=x)
            for x in change["new"].split(":")
        ]

        if (":" in change["new"]) and (":" in change["old"]):
            old2 = float(change["old"].split(":")[1])
            new2 = float(change["new"].split(":")[1])
            if old2 == new2:
                new = new[0], new[0] + 1
            else:
                new = new[1], new[1] + 1

        new = [min(max(x, self.min), self.max) for x in new]
        if len(new) == 1:
            new = [new[0], new[0] + 1]
        self._lock = True
        self._widget.value = " : ".join(f"{self._coord[x]:{self._fmt}}" for x in new)
        self.value = new
        self._lock = False

    def _on_value_change(self, change):
        if self._lock:
            return

        new = [min(max(x, self.min), self.max) for x in change["new"]]
        self._lock = True
        self._widget.value = " : ".join(f"{self._coord[x]:{self._fmt}}" for x in new)
        self._lock = False


class BoundsSingleWidget(ipw.HBox):
    def __init__(
        self,
        coord: sc.Variable,
        index: int,
    ):
        self._widget = BoundedText(
            continuous_update=False,
            coord=coord,
            index=index,
        )

        super().__init__([self._widget])

    @property
    def value(self) -> float:
        return (self._widget.value,)

    @value.setter
    def value(self, value: tuple[float]):
        self._widget.value = value[0]

    @property
    def string_value(self) -> str:
        return str(self._widget._widget.value)

    def set_observe_callback(self, callback: callable, **kwargs):
        self._widget.observe(callback, **kwargs)


class BoundsSingleBinEdgesWidget(ipw.HBox):
    def __init__(self, coord: sc.Variable, index: int):
        self._widget = BoundedBinEdgeText(
            continuous_update=False,
            coord=coord,
            index=index,
        )
        super().__init__([self._widget])

    @property
    def value(self) -> float:
        return self._widget.value

    @value.setter
    def value(self, value: tuple[float]):
        self._widget.value = value

    @property
    def string_value(self) -> str:
        return str(self._widget._widget.value)

    def set_observe_callback(self, callback: callable, **kwargs):
        self._widget.observe(callback, **kwargs)


class BoundsRangeWidget(ipw.HBox):
    def __init__(
        self,
        coord: sc.Variable,
        index: tuple[int, int],
    ):
        self._min_widget = BoundedText(
            continuous_update=False,
            coord=coord,
            index=index[0],
        )

        self._max_widget = BoundedText(
            continuous_update=False,
            coord=coord,
            index=index[1],
        )
        self._min_widget.observe(self._on_min_change, names='value')
        self._max_widget.observe(self._on_max_change, names='value')

        super().__init__([self._min_widget, ipw.Label(value=":"), self._max_widget])

    def set_observe_callback(self, callback: callable, **kwargs):
        self._min_widget.observe(callback, **kwargs)
        self._max_widget.observe(callback, **kwargs)

    def _on_min_change(self, change: dict):
        self._max_widget.min = change["new"]

    def _on_max_change(self, change: dict):
        self._min_widget.max = change["new"]

    @property
    def value(self) -> tuple[float, float]:
        return self._min_widget.value, self._max_widget.value

    @value.setter
    def value(self, value: tuple[float, float]):
        if value[0] > float(self._max_widget.value):
            self._max_widget.value = value[1]
            self._min_widget.value = value[0]
        else:
            self._min_widget.value = value[0]
            self._max_widget.value = value[1]

    @property
    def string_value(self) -> str:
        return f"{self._min_widget._widget.value} : {self._max_widget._widget.value}"


class DimSlicer(ipw.HBox):
    def __init__(
        self,
        dim: str,
        size: int,
        coord: sc.Variable,
        slider_constr: type[ipw.Widget],
        value: int | tuple[int, int] | None = None,
        enable_player: bool = False,
        width: str = "25em",
    ):
        self._kind = "single" if issubclass(slider_constr, ipw.IntSlider) else "range"
        if enable_player and (self._kind != "single"):
            raise TypeError(
                "Player can only be enabled for IntSlider, not for IntRangeSlider."
            )

        self.dim = dim
        self.coord = coord
        self._is_bin_edges = self.coord.sizes[dim] > size
        self.coord_min = self.coord.values[0]
        self.coord_max = self.coord.values[-1]

        if value is None:
            value = (size - 1) // 2 if self._kind == "single" else (0, size - 1)

        self.dim_label = ipw.Label(value=dim, layout={"margin": "0px 0px 0px 10px"})
        self.slider = slider_constr(
            step=1,
            min=0,
            max=size - 1,
            value=value,
            continuous_update=True,
            readout=False,
            layout={"width": width, "margin": "0px 10px 0px 10px"},
        )
        self.continuous_update = ipw.Checkbox(
            value=True,
            tooltip="Continuous update",
            indent=False,
            layout={"width": "1.52em"},
        )

        if self._kind == "range":
            self.bounds = BoundsRangeWidget(coord=self.coord, index=value)
        elif self._is_bin_edges:
            self.bounds = BoundsSingleBinEdgesWidget(coord=self.coord, index=value)
        else:
            self.bounds = BoundsSingleWidget(coord=self.coord, index=value)

        self.unit = ipw.Label("" if self.coord.unit is None else f"[{self.coord.unit}]")
        ipw.jslink(
            (self.continuous_update, 'value'), (self.slider, 'continuous_update')
        )

        children = [self.dim_label, self.slider, self.continuous_update, self.bounds]
        children.append(self.unit)
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

        self._bounds_lock = False
        self._update_label({"new": self.slider.value})
        self.slider.observe(self._update_label, names='value')
        self.bounds.set_observe_callback(self._move_slider_to_label, names='value')

        super().__init__(children)

    def _update_label(self, change: dict):
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
        self._bounds_lock = True
        self.bounds.value = np.atleast_1d(inds).tolist()
        self._bounds_lock = False

    def _move_slider_to_label(self, change: dict):
        """
        Move the slider to the position corresponding to the coordinate value in the
        label, if possible.
        """
        if self._bounds_lock:
            return
        inds = self.bounds.value
        if len(inds) == 1:
            self.slider.value = inds[0]
        else:
            if self._kind == "range":
                self.slider.value = inds
            else:
                self.slider.value = inds[0]

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
            dim=dim,
            size=size,
            coord=coord,
            slider_constr=ipw.IntSlider,
            value=0,
            width=width,
        )

        self.range_slicer = DimSlicer(
            dim=dim, size=size, coord=coord, slider_constr=ipw.IntRangeSlider
        )

        self.int_slicer.slider.observe(self.move_range, names='value')

        self.slider_toggler = ipw.ToggleButtons(
            options=["o-o", "-o-"],
            tooltips=['Range slider', 'Single handle slider'],
            style={"button_width": "3.2em"},
        )
        self.slider_toggler.observe(self.toggle_slider_mode, names='value')

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
    def dim_label(self) -> ipw.Label:
        return self.range_slicer.dim_label

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
        width: str = "25em",
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
                width=width,
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
width:
    The width of the sliders. Defaults to "25em".

    .. versionadded:: 25.07.0
"""

RangeSliceWidget = partial(
    _BaseSliceWidget,
    slider_constr=ipw.IntRangeSlider,
    slicer_constr=DimSlicer,
    enable_player=False,
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
width:
    The width of the sliders. Defaults to "25em".
"""

CombinedSliceWidget = partial(
    _BaseSliceWidget,
    slider_constr=None,
    slicer_constr=CombinedSlicer,
    enable_player=False,
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
width:
    The width of the sliders. Defaults to "25em".
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
