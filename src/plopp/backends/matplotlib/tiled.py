# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from __future__ import annotations

from typing import Any, Literal, NamedTuple

import numpy as np
from matplotlib import gridspec
from matplotlib.gridspec import SubplotSpec
from matplotlib.layout_engine import ConstrainedLayoutEngine

from ...core.typing import FigureLike
from .canvas import Canvas
from .utils import make_figure

ShareMode = bool | Literal['all', 'row', 'col', 'none']

_SHARE_MODES = ('all', 'row', 'col', 'none')


class _LabelRule(NamedTuple):
    """
    How the redundant tick labels of one axis direction are identified.
    """

    #: Sharing modes that make the labels of inner tiles redundant.
    modes: tuple[str, ...]
    #: Predicate on :class:`matplotlib.gridspec.SubplotSpec` selecting the tiles that
    #: keep their labels.
    at_edge: str
    #: Key of ``Axes.tick_params`` toggling the labels.
    tick_param: str


#: An x-axis label is repeated down a column, so it may only be dropped if the tiles of
#: a column are shared; likewise a y-axis label is repeated across a row.
_LABEL_RULES = {
    'x': _LabelRule(('all', 'col'), 'is_last_row', 'labelbottom'),
    'y': _LabelRule(('all', 'row'), 'is_first_col', 'labelleft'),
}


def _parse_share(mode: ShareMode, name: str) -> str:
    """
    Normalize a sharing mode to one of ``'all'``, ``'row'``, ``'col'``, ``'none'``.
    """
    mode = {True: 'all', False: 'none'}.get(mode, mode)
    if mode not in _SHARE_MODES:
        raise ValueError(
            f"Invalid value for {name}: {mode!r}. "
            f"Expected a bool or one of {_SHARE_MODES}."
        )
    return mode


def _group_key(mode: str, spec: SubplotSpec) -> int:
    """
    Identify the group of tiles a subplot belongs to. Tiles spanning multiple rows or
    columns are assigned to the group of the first row/column they span.
    """
    if mode == 'all':
        return 0
    span = spec.rowspan if mode == 'row' else spec.colspan
    return span.start


def _axis_props(canvas: Canvas, direction: str) -> tuple:
    """
    The properties that must agree between tiles for their axes to be shared.

    For one-dimensional figures the vertical axis carries the data (not a coordinate),
    in which case the dimension is ``None`` and the unit is that of the data.
    """
    return (
        canvas.dims.get(direction),
        canvas.units.get(direction, canvas.units.get('data')),
        getattr(canvas, f'{direction}scale'),
    )


def _union(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
    """
    Smallest range containing both ``a`` and ``b``, preserving the direction of ``a``.
    """
    lo = min(*a, *b)
    hi = max(*a, *b)
    return (hi, lo) if a[0] > a[1] else (lo, hi)


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
    hspace:
        Vertical space between tiles, as a fraction of the tile height. Defaults to
        zero when x tick labels are dropped from inner tiles.
    wspace:
        Horizontal space between tiles, as a fraction of the tile width. Defaults to
        zero when y tick labels are dropped from inner tiles.
    sharex:
        Share the x-axis between tiles: ``'all'`` (or ``True``) for the entire grid,
        ``'col'`` within each column, ``'row'`` within each row, ``'none'`` (or
        ``False``) to disable. Tiles sharing an axis are required to have the same
        dimension, unit and scale, and are given a common range. With ``'all'`` and
        ``'col'`` the x tick labels are drawn on the bottom row only.
    sharey:
        Same as ``sharex``, for the y-axis. With ``'all'`` and ``'row'`` the y tick
        labels are drawn on the left column only.
    **kwargs:
        Additional arguments passed to :class:`matplotlib.gridspec.GridSpec`.

    Notes
    -----
    Sharing is not propagated by the ``+`` and ``/`` operators: combining two tiled
    figures yields an unshared figure, as their sharing modes may disagree and their
    axes need not be compatible. A tile of a figure with shared axes also cannot be
    replaced, since Matplotlib provides no way to un-share axes.

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

    Create a tiled figure where all tiles share the same axes:

      >>> tiled = pp.tiled(2, 2, sharex=True, sharey=True)

    """

    def __init__(
        self,
        nrows: int,
        ncols: int,
        figsize: tuple[float, float] | None = None,
        hspace: float | None = None,
        wspace: float | None = None,
        sharex: ShareMode = False,
        sharey: ShareMode = False,
        **kwargs: Any,
    ) -> None:
        self.nrows = nrows
        self.ncols = ncols
        self._share = {
            'x': _parse_share(sharex, 'sharex'),
            'y': _parse_share(sharey, 'sharey'),
        }
        self._share_refs = {'x': {}, 'y': {}}
        self.fig = make_figure(
            figsize=(
                (min(6.0 * ncols, 15.0), min(4.0 * nrows, 15.0))
                if figsize is None
                else figsize
            ),
            layout='constrained',
        )

        is_widget_backend = hasattr(self.fig.canvas, "on_widget_constructed")
        if hspace is None:
            hspace = (
                0.0 if self._hides_labels('x') else (0.2 if is_widget_backend else 0.02)
            )
        if wspace is None:
            wspace = (
                0.0 if self._hides_labels('y') else (0.2 if is_widget_backend else 0.05)
            )

        # Constrained layout pads every tile by w_pad/h_pad inches, which would keep
        # the tiles apart even at zero grid spacing. The padding is only dropped in the
        # direction where tiles are meant to sit flush; the outer margin it also
        # provides is not needed, as figures are rendered with a tight bounding box.
        self._pads = self.fig.get_layout_engine().get()
        pads = {}
        if self._hides_labels('x'):
            pads['h_pad'] = 0.0
        if self._hides_labels('y'):
            pads['w_pad'] = 0.0
        self._set_pads(**pads)

        self.gs = gridspec.GridSpec(
            nrows, ncols, figure=self.fig, wspace=wspace, hspace=hspace, **kwargs
        )
        self.figures = np.full((nrows, ncols), None)
        self._history = []

    def __setitem__(
        self,
        inds: int | slice | tuple[int, int] | tuple[slice, slice],
        fig: FigureLike,
    ) -> None:
        if any(m != 'none' for m in self._share.values()) and any(
            f is not None for f in np.atleast_1d(self.figures[inds]).ravel()
        ):
            raise ValueError(
                'Cannot replace a tile of a figure with shared axes: Matplotlib '
                'cannot un-share axes, so the replaced tile would stay joined to '
                'its neighbours. Build a new tiled figure instead.'
            )
        new_fig = fig.copy(ax=self.fig.add_subplot(self.gs[inds]))
        self._share_axes(new_fig)
        self._make_room_for_decorations(new_fig)
        self.figures[inds] = new_fig
        self._history.append((inds, new_fig))

    def _make_room_for_decorations(self, fig: FigureLike) -> None:
        """
        Take back the padding that flush tiles give up, for decorations that end up
        between two tiles: a title sits above its axes, a colorbar to the right of it.
        Without padding these touch the frame of the neighbouring tile and read as
        belonging to it.
        """
        pads = {}
        if fig.canvas.title:
            pads['h_pad'] = self._pads['h_pad']
        if fig.canvas.cax is not None:
            pads['w_pad'] = self._pads['w_pad']
        self._set_pads(**pads)

    def _set_pads(self, **pads: float) -> None:
        """
        Adjust the padding of the constrained layout, if the figure still uses one.
        Rendering a figure as a widget replaces the layout engine with a placeholder
        that cannot be configured.
        """
        engine = self.fig.get_layout_engine()
        if pads and isinstance(engine, ConstrainedLayoutEngine):
            engine.set(**pads)

    def _share_axes(self, fig: FigureLike) -> None:
        """
        Join the axes of a newly added tile to those of the other tiles in its group,
        and strip axis decorations that are now redundant.

        Matplotlib's ``Axes.sharex`` performs no compatibility checks and makes the
        joined axes adopt the reference's range and scale, so both the validation and
        the range union have to be done here.
        """
        ax = fig.ax
        spec = ax.get_subplotspec()
        for direction, mode in self._share.items():
            if mode == 'none':
                continue
            refs = self._share_refs[direction]
            key = _group_key(mode, spec)
            if (ref := refs.setdefault(key, fig)) is not fig:
                self._join(direction, ref=ref, fig=fig)
        for direction, rule in _LABEL_RULES.items():
            if not self._hides_labels(direction):
                continue
            # Tiles are placed flush against each other, so outward ticks would poke
            # into the neighbouring tile.
            ax.tick_params(axis=direction, which='both', direction='in')
            if not getattr(spec, rule.at_edge)():
                setattr(fig.canvas, f'{direction}label', '')
                ax.tick_params(**{rule.tick_param: False})

    def _hides_labels(self, direction: str) -> bool:
        return self._share[direction] in _LABEL_RULES[direction].modes

    @staticmethod
    def _join(direction: str, ref: FigureLike, fig: FigureLike) -> None:
        props = _axis_props(fig.canvas, direction)
        ref_props = _axis_props(ref.canvas, direction)
        if props != ref_props:
            names = ('dim', 'unit', 'scale')
            diff = ', '.join(
                f'{n}: {a} != {b}'
                for n, a, b in zip(names, props, ref_props, strict=True)
                if a != b
            )
            raise ValueError(
                f'Cannot share the {direction}-axis between tiles: {diff}. '
                f'Use share{direction}=False, or a mode that does not place these '
                'tiles in the same group.'
            )
        # Joining makes the axes adopt the reference's range, so the tile's own range
        # has to be read before, and folded back in after.
        rng = f'{direction}range'
        limits = getattr(fig.canvas, rng)
        getattr(fig.ax, f'share{direction}')(ref.ax)
        setattr(fig.canvas, rng, _union(limits, getattr(ref.canvas, rng)))

    def __getitem__(
        self, inds: int | slice | tuple[int, int] | tuple[slice, slice]
    ) -> FigureLike:
        return self.figures[inds]

    def _repr_mimebundle_(self, *args, **kwargs) -> dict:
        """
        Mimebundle display representation for jupyter notebooks.
        """
        return self.figures.ravel()[0]._repr_mimebundle_(*args, **kwargs)

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
