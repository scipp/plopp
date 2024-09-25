# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)
from __future__ import annotations

from matplotlib.axes import Axes
from matplotlib.figure import Figure as MplFigure

from ...graphics import BaseFig
from .canvas import Canvas
from .utils import fig_to_bytes

try:
    from ipywidgets import VBox
except ImportError:
    VBox = object


class MplBaseFig(BaseFig):
    """
    Mixin class for Matplotlib figures
    """

    def __init_figure__(self, View, *args, **kwargs):
        self.view = View(*args, **kwargs)
        # Saving the following is necessary for making copies of the figure
        self._view_maker = View
        self._args = args
        self._kwargs = kwargs

    @property
    def fig(self) -> MplFigure:
        """
        Get the underlying Matplotlib figure.
        """
        return self.view.canvas.fig

    @property
    def ax(self) -> Axes:
        """
        Get the underlying Matplotlib axes.
        """
        return self.view.canvas.ax

    @property
    def cax(self) -> Axes:
        """
        Get the underlying Matplotlib colorbar axes.
        """
        return self.view.canvas.cax

    def save(self, filename: str, **kwargs):
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
        return self.view.canvas.save(filename, **kwargs)

    def __add__(self, other):
        from .tiled import hstack

        return hstack(self, other)

    def __truediv__(self, other):
        from .tiled import vstack

        return vstack(self, other)

    def copy(self, ax: Axes | None = None) -> MplBaseFig:
        """
        Create a copy of the figure.

        Parameters
        ----------
        ax:
            The axes to use for the new figure. If ``None``, new axes will be created.
        """
        kwargs = self._kwargs.copy()
        kwargs.update(ax=ax)
        kwargs.update(
            dims=self.view._dims,
            canvas_maker=Canvas,
            artist_maker=self.view._artist_maker,
        )
        out = self.__class__(
            self._view_maker,
            *self._args,
            **kwargs,
        )
        for prop in ('xrange', 'yrange', 'xscale', 'yscale', 'title', 'grid'):
            setattr(out.canvas, prop, getattr(self.canvas, prop))
        return out

    def show(self):
        """
        Make a call to Matplotlib's underlying ``show`` function.
        """
        self.fig.show()


def _make_png_repr(fig):
    return {'image/png': fig_to_bytes(fig, form='png')}


def _make_svg_repr(fig):
    return {'image/svg+xml': fig_to_bytes(fig, form='svg').decode()}


REPR_MAP = {'png': _make_png_repr, 'svg': _make_svg_repr}


def get_repr_maker(form=None, npoints=0):
    """
    Get the function used to create the mimebundle representation of a figure,
    based on the format requested and the number of points in the figure.
    """
    if form is None:
        form = 'png' if (npoints > 20_000) else 'svg'
    return REPR_MAP[form.lower()]


class InteractiveFigure(MplBaseFig, VBox):
    """
    Create an interactive Matplotlib figure.
    """

    def __init__(self, View, *args, **kwargs):
        from ...widgets import HBar, VBar, make_toolbar_canvas2d

        self.__init_figure__(View, *args, **kwargs)
        self.interactive = True
        self.toolbar = make_toolbar_canvas2d(view=self.view)
        self.left_bar = VBar([self.toolbar])
        self.right_bar = VBar()
        self.bottom_bar = HBar()
        self.top_bar = HBar()
        super().__init__(self._make_children())

    def __repr__(self) -> str:
        self.children = self._make_children()
        return super().__repr__()

    def _make_children(self):
        from ...widgets import HBar

        return [
            self.top_bar,
            HBar([self.left_bar, self.view.canvas.to_widget(), self.right_bar]),
            self.bottom_bar,
        ]


class StaticFigure(MplBaseFig):
    """
    Create a static Matplotlib figure.
    The output will be either svg or png, depending on the number of drawn onto the
    canvas.
    """

    def __init__(self, View, *args, **kwargs):
        self.__init_figure__(View, *args, **kwargs)
        self.interactive = False

    def _repr_mimebundle_(self, include=None, exclude=None) -> dict:
        """
        Mimebundle display representation for jupyter notebooks.
        """
        str_repr = str(self.fig)
        out = {'text/plain': str_repr[:-1] + f', {len(self.artists)} artists)'}
        if self.view._repr_format is not None:
            repr_maker = get_repr_maker(form=self.view._repr_format)
        else:
            npoints = sum(len(line.get_xdata()) for line in self.view.canvas.ax.lines)
            repr_maker = get_repr_maker(npoints=npoints)
        out.update(repr_maker(self.view.canvas.fig))
        return out

    def to_widget(self):
        """
        Convert the Matplotlib figure to an image widget.
        """
        return self.view.canvas.to_image()


def Figure(*args, **kwargs):
    from .utils import is_interactive_backend

    if is_interactive_backend():
        return InteractiveFigure(*args, **kwargs)
    else:
        return StaticFigure(*args, **kwargs)
