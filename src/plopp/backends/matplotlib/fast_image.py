# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Scipp contributors (https://github.com/scipp)

import uuid
import warnings
from typing import Literal

import numpy as np
import scipp as sc

from ...core.utils import coord_as_bin_edges, scalar_to_string
from ...graphics.bbox import BoundingBox, axis_bounds
from ...graphics.colormapper import ColorMapper
from ..common import check_ndim
from .canvas import Canvas


class FastImage:
    """
    Artist to represent two-dimensional data.

    Parameters
    ----------
    canvas:
        The canvas that will display the image.
    colormapper:
        The colormapper to use for the image.
    data:
        The initial data to create the image from.
    artist_number:
        The canvas keeps track of how many images have been added to it. This is unused
        by the FastImage artist.
    uid:
        The unique identifier of the artist. If None, a random UUID is generated.
    **kwargs:
        Additional arguments are forwarded to Matplotlib's ``imshow``.
    """

    def __init__(
        self,
        canvas: Canvas,
        colormapper: ColorMapper,
        data: sc.DataArray,
        artist_number: int,
        uid: str | None = None,
        **kwargs,
    ):
        check_ndim(data, ndim=2, origin="FastImage")
        self.uid = uid if uid is not None else uuid.uuid4().hex
        self._canvas = canvas
        self._colormapper = colormapper
        self._ax = self._canvas.ax
        self._data = data

        string_labels = {}
        self._bin_edge_coords = {}
        for i, k in enumerate("yx"):
            self._bin_edge_coords[k] = coord_as_bin_edges(
                self._data, self._data.dims[i]
            )
            if self._data.coords[self._data.dims[i]].dtype == str:
                string_labels[k] = self._data.coords[self._data.dims[i]]

        self._xmin, self._xmax = self._bin_edge_coords["x"].values[[0, -1]]
        self._ymin, self._ymax = self._bin_edge_coords["y"].values[[0, -1]]
        self._dx = np.diff(self._bin_edge_coords["x"].values[:2])
        self._dy = np.diff(self._bin_edge_coords["y"].values[:2])

        # Calling imshow sets the aspect ratio to 'equal', which might not be what the
        # user requested. We need to restore the original aspect ratio after making the
        # image.
        original_aspect = self._ax.get_aspect()

        # Because imshow sets the aspect, it may generate warnings when the axes scales
        # are log.
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                category=UserWarning,
                message="Attempt to set non-positive .* on a log-scaled axis",
            )
            self._image = self._ax.imshow(
                self._data.values,
                origin="lower",
                extent=(self._xmin, self._xmax, self._ymin, self._ymax),
                **({"interpolation": "nearest"} | kwargs),
            )

        self._ax.set_aspect(original_aspect)
        self._colormapper.add_artist(self.uid, self)
        self._update_colors()

        for xy, var in string_labels.items():
            getattr(self._ax, f"set_{xy}ticks")(np.arange(float(var.shape[0])))
            getattr(self._ax, f"set_{xy}ticklabels")(var.values)

        self._canvas.register_format_coord(self.format_coord)
        # We also hide the cursor hover values generated by the image, as values are
        # included in our custom format_coord.
        self._image.format_cursor_data = lambda _: ""

    @property
    def data(self):
        """
        Get the image's data in a form that may have been tweaked, compared to the
        original data, in the case of a two-dimensional coordinate.
        """
        return self._data

    def notify_artist(self, message: str) -> None:
        """
        Receive notification from the colormapper that its state has changed.
        We thus need to update the colors of the image.

        Parameters
        ----------
        message:
            The message from the colormapper.
        """
        self._update_colors()

    def _update_colors(self):
        """
        Update the image colors.
        """
        rgba = self._colormapper.rgba(self.data)
        self._image.set_data(rgba)

    def update(self, new_values: sc.DataArray):
        """
        Update image array with new values.

        Parameters
        ----------
        new_values:
            New data to update the image values from.
        """
        check_ndim(new_values, ndim=2, origin="FastImage")
        self._data = new_values
        self._update_colors()

    def format_coord(
        self, xslice: tuple[str, sc.Variable], yslice: tuple[str, sc.Variable]
    ) -> str:
        """
        Format the coordinates of the mouse pointer to show the value of the
        data at that point.

        Parameters
        ----------
        xslice:
            Dimension and x coordinate of the mouse pointer, as slice parameters.
        yslice:
            Dimension and y coordinate of the mouse pointer, as slice parameters.
        """
        ind_x = int((xslice[1].value - self._xmin) / self._dx)
        ind_y = int((yslice[1].value - self._ymin) / self._dy)
        try:
            val = self._data[yslice[0], ind_y][xslice[0], ind_x]
            prefix = self._data.name
            if prefix:
                prefix += ": "
            return prefix + scalar_to_string(val)
        except IndexError:
            return None

    @property
    def visible(self) -> bool:
        """
        The visibility of the image.
        """
        return self._image.get_visible()

    @visible.setter
    def visible(self, val: bool):
        self._image.set_visible(val)

    @property
    def opacity(self) -> float:
        """
        The opacity of the image.
        """
        return self._image.get_alpha()

    @opacity.setter
    def opacity(self, val: float):
        self._image.set_alpha(val)

    def bbox(self, xscale: Literal["linear", "log"], yscale: Literal["linear", "log"]):
        """
        The bounding box of the image.
        """
        return BoundingBox(
            **{**axis_bounds(("xmin", "xmax"), self._bin_edge_coords["x"], xscale)},
            **{**axis_bounds(("ymin", "ymax"), self._bin_edge_coords["y"], yscale)},
        )

    def remove(self):
        """
        Remove the image artist from the canvas.
        """
        self._image.remove()
        self._colormapper.remove_artist(self.uid)
