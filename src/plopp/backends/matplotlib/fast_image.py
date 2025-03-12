# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

import uuid
from typing import Literal

import numpy as np
import scipp as sc
from matplotlib.image import AxesImage

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
        uid: str | None = None,
        **kwargs,
    ):
        check_ndim(data, ndim=2, origin="FastImage")
        self.uid = uid if uid is not None else uuid.uuid4().hex
        self._canvas = canvas
        self._colormapper = colormapper
        self._ax = self._canvas.ax
        self._data = data
        # Because all keyword arguments from the figure are forwarded to both the canvas
        # and the line, we need to remove the arguments that belong to the canvas.
        kwargs.pop("ax", None)
        kwargs.pop("cax", None)
        # An artist number is passed to the artist, but is unused for the image.
        kwargs.pop("artist_number", None)

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

        self._image = AxesImage(
            self._ax,
            origin="lower",
            extent=(self._xmin, self._xmax, self._ymin, self._ymax),
            **({"interpolation": "nearest"} | kwargs),
        )
        self._image.set_data(self._data.values)
        self._ax.add_image(self._image)

        # self._image = self._ax.imshow(
        #     ,
        #     extent=(self._xmin, self._xmax, self._ymin, self._ymax),
        #     origin="lower",
        #     **kwargs,
        # )

        self._colormapper.add_artist(self.uid, self)
        self._update_colors()

        for xy, var in string_labels.items():
            getattr(self._ax, f"set_{xy}ticks")(np.arange(float(var.shape[0])))
            getattr(self._ax, f"set_{xy}ticklabels")(var.values)

        self._canvas.register_format_coord(self.format_coord)

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

    def bbox(self, xscale: Literal["linear", "log"], yscale: Literal["linear", "log"]):
        """
        The bounding box of the image.
        """
        # return BoundingBox(
        #     xmin=self._xmin, xmax=self._xmax, ymin=self._ymin, ymax=self._ymax
        # )
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
