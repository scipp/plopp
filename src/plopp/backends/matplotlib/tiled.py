# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from __future__ import annotations

from typing import Any

import numpy as np
from matplotlib import gridspec

from ...core.typing import FigureLike
from .figure import get_repr_maker
from .utils import is_interactive_backend, make_figure


class Tiled:
    """
    A tiled figure.
    This is based on Matpotlib's GridSpec.

    .. versionadded:: 23.08.0

    Parameters
    ----------
    nrows:
        Number of rows.
    ncols:
        Number of columns.
    figsize:
        Figure size (width, height) in inches.
    **kwargs:
        Additional arguments passed to :class:`matplotlib.gridspec.GridSpec`.

    Examples
    --------
    Create a tiled figure with two plots stacked vertically:

      >>> da1 = pp.data.data1d()
      >>> da2 = pp.data.data2d()
      >>> tiled = pp.tiled(2, 1)
      >>> tiled[0] = da1.plot()
      >>> tiled[1] = da2.plot()

    Create a tiled 2x2 figure:

      >>> da1 = pp.data.data1d()
      >>> da2 = pp.data.data2d()
      >>> da3 = pp.data.data2d()
      >>> da4 = pp.data.data1d()
      >>> tiled = pp.tiled(2, 2)
      >>> tiled[0, 0] = da1.plot()
      >>> tiled[0, 1] = da2.plot()
      >>> tiled[1, 0] = da3.plot()
      >>> tiled[1, 1] = da4.plot()

    Create a tiled figure with two figures side by side and the first is twice as wide:

      >>> da1 = pp.data.data1d()
      >>> da2 = pp.data.data2d()
      >>> tiled = pp.tiled(1, 3)
      >>> tiled[0, :2] = da1.plot()
      >>> tiled[0, 2] = da2.plot()

    """

    def __init__(
        self,
        nrows: int,
        ncols: int,
        figsize: tuple[float, float] | None = None,
        **kwargs: Any,
    ) -> None:
        self.nrows = nrows
        self.ncols = ncols
        self.fig = make_figure(
            figsize=(
                (min(6.0 * ncols, 15.0), min(4.0 * nrows, 15.0))
                if figsize is None
                else figsize
            ),
            layout='constrained',
        )

        self.gs = gridspec.GridSpec(nrows, ncols, figure=self.fig, **kwargs)
        self.figures = np.full((nrows, ncols), None)
        self._history = []

    def __setitem__(
        self,
        inds: int | slice | tuple[int, int] | tuple[slice, slice],
        fig: FigureLike,
    ) -> None:
        new_fig = fig.copy(ax=self.fig.add_subplot(self.gs[inds]))
        self.figures[inds] = new_fig
        self._history.append((inds, new_fig))

    def __getitem__(
        self, inds: int | slice | tuple[int, int] | tuple[slice, slice]
    ) -> FigureLike:
        return self.figures[inds]

    def _repr_mimebundle_(self, include=None, exclude=None) -> dict:
        """
        Mimebundle display representation for jupyter notebooks.
        """
        if is_interactive_backend():
            return self.fig.canvas._repr_mimebundle_(include=include, exclude=exclude)
        else:
            out = {'text/plain': f'TiledFigure(nrows={self.nrows}, ncols={self.ncols})'}
            npoints = sum(
                len(line.get_xdata()) for ax in self.fig.get_axes() for line in ax.lines
            )
            out.update(get_repr_maker(npoints=npoints)(self.fig))
            return out

    def save(self, filename: str, **kwargs: Any) -> None:
        """
        Save the figure to file.
        The default directory for writing the file is the same as the
        directory where the script or notebook is running.

        Parameters
        ----------
        filename:
            Name of the output file. Possible file extensions are ``.jpg``, ``.png``,
            ``.svg``, and ``.pdf``.
        """
        self.fig.savefig(filename, **{**{'bbox_inches': 'tight'}, **kwargs})

    def show(self) -> None:
        """
        Make a call to Matplotlib's underlying ``show`` function.
        """
        self.fig.show()

    def __add__(self, other: Tiled) -> Tiled:
        if not isinstance(other, self.__class__):
            t = Tiled(1, 1)
            t[0, 0] = other
            other = t

        out = Tiled(nrows=max(self.nrows, other.nrows), ncols=self.ncols + other.ncols)
        for inds, view in self._history:
            out[inds] = view
        for inds, view in other._history:
            out[inds[0], inds[1] + self.ncols] = view
        return out

    def __truediv__(self, other: Tiled) -> Tiled:
        if not isinstance(other, self.__class__):
            t = Tiled(1, 1)
            t[0, 0] = other
            other = t

        out = Tiled(nrows=self.nrows + other.nrows, ncols=max(self.ncols, other.ncols))
        for inds, view in self._history:
            out[inds] = view
        for inds, view in other._history:
            out[inds[0] + self.nrows, inds[1]] = view
        return out


def hstack(left: Tiled | FigureLike, right: Tiled | FigureLike) -> Tiled:
    """
    Display two views side by side.

    Parameters
    ----------
    left:
        The view to display on the left.
    right:
        The view to display on the right.
    """
    left_tiled = isinstance(left, Tiled)
    right_tiled = isinstance(right, Tiled)
    if (not left_tiled) and (not right_tiled):
        out = Tiled(1, 2)
        out[0, 0] = left
        out[0, 1] = right
        return out
    elif left_tiled:
        t = Tiled(1, 1)
        t[0, 0] = right
        return left + t
    else:
        t = Tiled(1, 1)
        t[0, 0] = left
        return t + right


def vstack(top: Tiled | FigureLike, bottom: Tiled | FigureLike) -> Tiled:
    """
    Display two views on top of each other.

    Parameters
    ----------
    top:
        The view to display on the top.
    bottom:
        The view to display on the bottom.
    """
    top_tiled = isinstance(top, Tiled)
    bottom_tiled = isinstance(bottom, Tiled)
    if (not top_tiled) and (not bottom_tiled):
        out = Tiled(2, 1)
        out[0, 0] = top
        out[1, 0] = bottom
        return out
    elif top_tiled:
        t = Tiled(1, 1)
        t[0, 0] = bottom
        return top / t
    else:
        t = Tiled(1, 1)
        t[0, 0] = top
        return t / bottom
