# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from functools import partial

# from typing import Any
import ipywidgets as ipw
import numpy as np
import scipp as sc
from traitlets import Any, Tuple

from ..core import node
from .box import VBar


def _round_float(x: float, prec=3) -> float:
    try:
        return round(x, prec)
    except TypeError:
        return x


# class BoundWidget(ipw.HBox, ipw.ValueWidget):
#     value = Any().tag(sync=True)

#     def __init__(self, coord: sc.Variable, value: float):
#         self._coord = coord
#         # self._child_lock = False
#         # self._value_lock = False
#         coord_min, coord_max = self._coord.values[0], self._coord.values[-1]
#         if self._coord.dtype != sc.DType.datetime64:
#             self._widget = ipw.BoundedFloatText(
#                 continuous_update=False,
#                 min=coord_min,
#                 max=coord_max,
#                 step=(coord_max - coord_min) / 999,
#                 value=value,
#                 layout={"width": "6em"},
#             )
#             self._is_float = True
#         else:
#             self._widget = ipw.Text(
#                 continuous_update=False, value=str(value), layout={"width": "10em"}
#             )
#             self._is_float = False

#         # observe user edits
#         self._widget.observe(self._on_child_change, names="value")
#         # observe external value changes
#         self.observe(self._on_value_change, names="value")

#         super().__init__([self._widget])
#         self.value = self._widget.value

#     def _on_child_change(self, change):
#         # print(
#         #     "BOUND, on_child_change: value_lock",
#         #     self._value_lock,
#         #     "child_lock",
#         #     self._child_lock,
#         # )
#         # if self._child_lock:
#         #     return
#         if self._widget.value == change["new"]:
#             return

#         self._value_lock = True
#         self.value = float(self._widget.value)
#         self._value_lock = False

#     # def _on_value_change(self, change):
#     #     if self._lock:
#     #         return

#     #     self._lock = True
#     #     if self._is_float:
#     #         self._widget.value = round(change["new"], 3)
#     #     else:
#     #         self._widget.value = str(change["new"])
#     #     self._lock = False

#     def _on_value_change(self, change):
#         # if self._is_float:
#         #     new = round(change["new"], 3)
#         # else:
#         #     new = str(change["new"])

#         # if new != self._widget.value:
#         #     self._widget.value = new
#         print(
#             "BOUND, on_VALUE_change: value_lock",
#             self._value_lock,
#             "child_lock",
#             self._child_lock,
#         )

#         if self._value_lock:
#             return

#         self._child_lock = True
#         if self._is_float:
#             self._widget.value = round(change["new"], 3)
#         else:
#             self._widget.value = str(change["new"])
#         self._child_lock = False

#     @property
#     def min(self) -> float | None:
#         return getattr(self._widget, "min", None)

#     @min.setter
#     def min(self, value: float):
#         if self._is_float:
#             self._widget.min = value

#     @property
#     def max(self) -> float | None:
#         return getattr(self._widget, "max", None)

#     @max.setter
#     def max(self, value: float):
#         if self._is_float:
#             self._widget.max = value

#     # def _on_subwidget_change(self, _=None):
#     #     """ """
#     #     if self._is_float:
#     #         self.value = round(value, 3)
#     #     else:
#     #         self._widget.value = str(value)
#     #     self.value = {dim: slicer.value for dim, slicer in self.controls.items()}

#     # @property
#     # def value(self) -> float:
#     #     return float(self._widget.value)

#     # @value.setter
#     # def value(self, value: float):
#     #     if self._is_float:
#     #         self._widget.value = round(value, 3)
#     #     else:
#     #         self._widget.value = str(value)

#     def get_closest_index(self) -> int:
#         """
#         Get the index of the coordinate value closest to the one in the widget.
#         """
#         # if self._is_float:
#         #     value = self.value
#         # else:
#         #     value = sc.scalar(self._widget.value, dtype=self._coord.dtype)
#         return np.argmin(np.abs(self._coord.values - self.value))


# # def _set_bound_widget_value(widget: ipw.Widget, value: float):
# #     if isinstance(widget, ipw.BoundedFloatText):
# #         widget.value = value
# #     elif isinstance(widget, ipw.Text):
# #         widget.value = str(value)


class BoundsSingleWidget(ipw.HBox):
    def __init__(
        self,
        coord: sc.Variable,
        index: int,
        # value: float,
    ):
        self._coord = coord
        coord_min, coord_max = self._coord.values[0], self._coord.values[-1]
        # self._child_lock = False
        # self._value_lock = False
        step = (coord_max - coord_min) / 999
        self._widget = ipw.BoundedFloatText(
            continuous_update=False,
            min=coord_min,
            max=coord_max,
            step=step,
            value=_round_float(self._coord.values[index]),
            layout={"width": "6em"},
        )

        # observe user edits
        # self._widget.observe(self._on_child_change, names="value")
        # observe external value changes
        # self.observe(self._on_value_change, names="value")

        super().__init__([self._widget])

    @property
    def value(self) -> float:
        return self._widget.value

    @value.setter
    def value(self, value: tuple[float]):
        self._widget.value = _round_float(value[0])

    def set_observe_callback(self, callback: callable, **kwargs):
        self._widget.observe(callback, **kwargs)

    def get_closest_indices(self) -> tuple[int]:
        return (np.argmin(np.abs(self._coord.values - self.value)),)


class BoundsSingleBinEdgesWidget(ipw.HBox):
    def __init__(self, coord: sc.Variable, index: int):
        # ind = coord.size
        self._coord = coord
        self._widget = ipw.Text(
            continuous_update=False,
            value=" : ".join(
                str(_round_float(self._coord.values[i])) for i in (index, index + 1)
            ),
            layout={"width": "12em"},
        )

    @property
    def value(self) -> float:
        if ":" in self._widget.value:
            return float(self._widget.value.split(":")[0])
        return float(self._widget.value)

    @value.setter
    def value(self, value: tuple[float]):
        self._widget.value = " : ".join(str(_round_float(v)) for v in value)

    def set_observe_callback(self, callback: callable, **kwargs):
        self._widget.observe(callback, **kwargs)

    def get_closest_indices(self) -> tuple[int]:
        return (np.argmin(np.abs(self._coord.values - self.value)),)


# TODO
# make a class BoundsRangeWidgetDatetime


# New plan:
# - 2 bound widgets for range slider
# - 1 bound widget for single value midpoints
# - 1 new widget with Text for single value with bin edges: separate edges of current bin with :
# - make corresponding widgets for datetime which use Text


class BoundsRangeWidget(ipw.HBox):
    # value = Tuple(Any(), Any()).tag(sync=True)
    # value = Any().tag(sync=True)

    def __init__(
        self,
        coord: sc.Variable,
        index: tuple[int, int],
        # value_min: float,
        # value_max: float,
    ):
        # coord_min, coord_max = coord.values[0], coord.values[-1]
        # self._child_lock = False
        # self._value_lock = False

        # self._min_widget = BoundWidget(coord=coord, value=coord.values[0])
        # self._max_widget = BoundWidget(coord=coord, value=coord.values[-1])

        self._coord = coord
        coord_min, coord_max = self._coord.values[0], self._coord.values[-1]
        step = (coord_max - coord_min) / 999

        self._min_widget = ipw.BoundedFloatText(
            continuous_update=False,
            min=coord_min,
            max=coord_max,
            step=step,
            value=_round_float(self._coord.values[index[0]]),
            layout={"width": "6em"},
        )
        self._min_widget.is_lower_bound = True

        self._max_widget = ipw.BoundedFloatText(
            continuous_update=False,
            min=coord_min,
            max=coord_max,
            step=step,
            value=_round_float(self._coord.values[index[1]]),
            layout={"width": "6em"},
        )
        print(
            "min val",
            self._min_widget.value,
            _round_float(self._coord.values[index[0]]),
        )
        print(
            "max val",
            self._max_widget.value,
            _round_float(self._coord.values[index[1]]),
        )
        self._max_widget.is_lower_bound = False

        ipw.link((self._min_widget, 'max'), (self._max_widget, 'value'))
        ipw.link((self._max_widget, 'min'), (self._min_widget, 'value'))
        # self._min_widget.observe(self._on_min_change, names='value')
        # self._max_widget.observe(self._on_max_change, names='value')

        # observe user edits
        # self._min_widget.observe(self._on_child_change, names="value")
        # self._max_widget.observe(self._on_child_change, names="value")
        # observe external value changes
        # self.observe(self._on_value_change, names="value")

        super().__init__([self._min_widget, ipw.Label(value=":"), self._max_widget])

        # self.value = self._min_widget.value, self._max_widget.value

    def set_observe_callback(self, callback: callable, **kwargs):
        self._min_widget.observe(callback, **kwargs)
        self._max_widget.observe(callback, **kwargs)

    # def _on_min_change(self, change: dict):
    #     if self._max_widget._is_float:
    #         self._max_widget.min = change["new"]

    # def _on_max_change(self, change: dict):
    #     if self._min_widget._is_float:
    #         self._min_widget.max = change["new"]

    # def _on_child_change(self, _):
    #     # # if self._max_widget._is_float:
    #     # self._max_widget.min = self._min_widget.value
    #     # # if self._min_widget._is_float:
    #     # self._min_widget.max = self._max_widget.value

    #     if self._widget.value == change["new"]:
    #         return

    #     if self._child_lock:
    #         return

    #     print("bounds ON_CHILD_CHANGE", self._min_widget.value, self._max_widget.value)
    #     self._value_lock = True
    #     self.value = self._min_widget.value, self._max_widget.value
    #     self._value_lock = False

    # def _on_value_change(self, change):
    #     print(
    #         "bounds on_value_change",
    #         self._min_widget.value,
    #         self._max_widget.value,
    #         'value_lock',
    #         self._value_lock,
    #     )
    #     if self._value_lock:
    #         return

    #     self._child_lock = True
    #     # self._widget.value = change["new"][0]
    #     if change["new"][0] > self._max_widget.value:
    #         self._max_widget.value = change["new"][1]
    #         self._min_widget.value = change["new"][0]
    #     else:
    #         self._min_widget.value = change["new"][0]
    #         self._max_widget.value = change["new"][1]
    #     self._child_lock = False

    @property
    def value(self) -> tuple[float, float]:
        return self._min_widget.value, self._max_widget.value

    @value.setter
    def value(self, value: tuple[float, float]):
        # new_bounds = tuple(_round_float(v) for v in self.coord[self.dim, inds].values)
        if value[0] > float(self._max_widget.value):
            self._max_widget.value = _round_float(value[1])
            self._min_widget.value = _round_float(value[0])
        else:
            self._min_widget.value = _round_float(value[0])
            self._max_widget.value = _round_float(value[1])

    def get_closest_indices(self) -> tuple[int, int]:
        return tuple(np.argmin(np.abs(self._coord.values - x)) for x in self.value)


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

        # if self._is_bin_edges or (self._kind == "range"):
        #     self.bounds = BoundsRangeWidget(coord=self.coord, index=value)
        # else:
        #     self.bounds = BoundsSingleWidget(coord=self.coord, index=value)
        if self._kind == "range":
            self.bounds = BoundsRangeWidget(coord=self.coord, index=value)
        elif self._is_bin_edges:
            self.bounds = BoundsSingleBinEdgesWidget(coord=self.coord, index=value)
        else:
            self.bounds = BoundsSingleWidget(coord=self.coord, index=value)

        # self.bound_min = _make_bound_widget(
        #     coord=self.coord,
        #     coord_min=self.coord_min,
        #     coord_max=self.coord_max,
        #     value=self.coord_min,
        # )
        # if self._is_bin_edges or (self._kind == "range"):
        #     self.bound_max = _make_bound_widget(
        #         coord=self.coord,
        #         coord_min=self.coord_min,
        #         coord_max=self.coord_max,
        #         value=self.coord_max,
        #     )
        #     ipw.link((self.bound_min, 'max'), (self.bound_max, 'value'))
        #     ipw.link((self.bound_max, 'min'), (self.bound_min, 'value'))
        # else:
        #     self.bound_max = None

        self.unit = ipw.Label(
            "" if self.coord.unit is None else f" [{self.coord.unit}]"
        )
        ipw.jslink(
            (self.continuous_update, 'value'), (self.slider, 'continuous_update')
        )

        children = [
            self.dim_label,
            self.slider,
            self.continuous_update,
            self.bounds,
        ]
        # if self.bound_max is not None:
        #     children.append(ipw.Label(value=":"))
        #     children.append(self.bound_max)
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
        print("updating label", change)
        inds = change["new"]
        if self._is_bin_edges:
            if isinstance(inds, tuple):
                inds = (inds[0], inds[1] + 1)
            else:
                inds = (inds, inds + 1)
        self._bounds_lock = True
        # if isinstance(inds, tuple):
        #     new_bounds = tuple(
        #         _round_float(v) for v in self.coord[self.dim, inds].values
        #     )
        #     if new_bounds[0] > float(self.bound_max.value):
        #         self.bound_max.value = str(new_bounds[1])
        #         self.bound_min.value = str(new_bounds[0])
        #     else:
        #         self.bound_min.value = str(new_bounds[0])
        #         self.bound_max.value = str(new_bounds[1])
        # else:
        #     self.bound_min.value = str(_round_float(self.coord[self.dim, inds].value))
        # if isinstance(inds, tuple):
        #     new_bounds = self.coord[self.dim, inds].values

        # else:
        #     new_bounds = self.coord[self.dim, inds].value
        print("updating bounds", inds, self.bounds.value)
        self.bounds.value = np.atleast_1d(self.coord[self.dim, inds].values).tolist()
        self._bounds_lock = False

    def _move_slider_to_label(self, change: dict):
        """
        Move the slider to the position corresponding to the coordinate value in the
        label, if possible.
        """
        # print("move slider to label", change["new"])
        if self._bounds_lock:
            return
        # # Find the index of the coordinate value closest to the one in the label.
        # if self.bound_max is None:
        #     self.slider.value = np.argmin(np.abs(self.coord.values - change["new"]))
        # else:
        #     # vmin, vmax = self.bound_min.value, self.bound_max.value
        #     # bounds = tuple(
        #     #     np.argmin(np.abs(self.coord.values - x)) for x in (vmin, vmax)
        #     # )
        inds = self.bounds.get_closest_indices()
        if len(inds) == 1:
            self.slider.value = inds[0]
        else:
            if self._kind == "range":
                self.slider.value = inds
            else:
                # Here it means that the user has entered a range in the label,
                # but the slider is a single slider. We move the slider to the value
                # requested by the bound that was changed.
                if change["owner"].is_lower_bound:
                    self.slider.value = inds[0]
                else:
                    self.slider.value = inds[1]

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
