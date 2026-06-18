# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from typing import Any, Literal

import scipp as sc

from ...graphics.bbox import BoundingBox
from ...utils import parse_mutually_exclusive


class Canvas:
    """ """

    def __init__(
        self,
        figsize: tuple[float, float] | None = None,
        title: str | None = None,
        grid: bool = False,
        aspect: Literal['auto', 'equal'] | None = None,
        cbar: bool = False,
        user_vmin: sc.Variable | float | None = None,
        user_vmax: sc.Variable | float | None = None,
        xmin: sc.Variable | float | None = None,
        xmax: sc.Variable | float | None = None,
        ymin: sc.Variable | float | None = None,
        ymax: sc.Variable | float | None = None,
        logx: bool = False,
        logy: bool = False,
        xlabel: str | None = None,
        ylabel: str | None = None,
        norm: Literal['linear', 'log'] | None = None,
        **ignored,
    ):
        ymin = parse_mutually_exclusive(vmin=user_vmin, ymin=ymin)
        ymax = parse_mutually_exclusive(vmax=user_vmax, ymax=ymax)
        logy = parse_mutually_exclusive(norm=norm, logy=logy)

        self.bbox = BoundingBox()
        self.figsize = (6.0, 4.0) if figsize is None else figsize
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.grid = grid
        self.aspect = aspect
        self.cbar = cbar
        self.title = title
        self.xscale = 'log' if logx else 'linear'
        self.yscale = 'log' if logy else 'linear'

        self.dims = {}
        self.units = {}

    def draw(self):
        return

    def save(self, filename: str):
        # TODO: save to json blob
        pass

    def set_axes(
        self, dims: dict[str, int], units: dict[str, str], dtypes: dict[str, Any]
    ) -> None:
        """
        Set the axes dimensions and units.

        Parameters
        ----------
        dims:
            The dimensions of the data.
        units:
            The units of the data.
        dtypes:
            The data types of the data.
        """
        self.units = units
        self.dims = dims
        self.dtypes = dtypes

    @property
    def empty(self) -> bool:
        """
        Check if the canvas is empty.
        """
        return not self.dims

    @property
    def xrange(self) -> tuple[float, float]:
        """
        Get the range/limits of the x-axis.
        """
        return (self.xmin, self.xmax)

    @xrange.setter
    def xrange(self, value: tuple[float, float]):
        self.xmin, self.xmax = value

    @property
    def yrange(self) -> tuple[float, float]:
        """
        Get the range/limits of the y-axis.
        """
        return (self.ymin, self.ymax)

    @yrange.setter
    def yrange(self, value: tuple[float, float]):
        self.ymin, self.ymax = value

    def update_legend(self):
        pass

    def has_user_xlabel(self) -> bool:
        """
        Return ``True`` if the user has set an x-axis label.
        """
        return self.xlabel is not None

    def has_user_ylabel(self) -> bool:
        """
        Return ``True`` if the user has set a y-axis label.
        """
        return self.ylabel is not None

    def as_json(self):
        """
        Convert the canvas to a JSON serializable format.
        """
        return {
            "figsize": self.figsize,
            "title": self.title,
            "grid": self.grid,
            "aspect": self.aspect,
            "cbar": self.cbar,
            "xrange": self.xrange,
            "yrange": self.yrange,
            "xlabel": self.xlabel,
            "ylabel": self.ylabel,
            "xscale": self.xscale,
            "yscale": self.yscale,
        }
