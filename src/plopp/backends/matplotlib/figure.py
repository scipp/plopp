# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

from ...graphics import BaseFig
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
        self._view = View(*args, **kwargs)
        self._args = args
        self._kwargs = kwargs

    @property
    def fig(self):
        """
        Get the underlying Matplotlib figure.
        """
        return self._view.canvas.fig

    @property
    def ax(self):
        """
        Get the underlying Matplotlib axes.
        """
        return self._view.canvas.ax

    @property
    def cax(self):
        """
        Get the underlying Matplotlib colorbar axes.
        """
        return self._view.canvas.cax

    def save(self, filename, **kwargs):
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
        return self._view.canvas.save(filename, **kwargs)

    def __add__(self, other):
        from .tiled import hstack

        return hstack(self, other)

    def __truediv__(self, other):
        from .tiled import vstack

        return vstack(self, other)


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


# def Figure(*args, **kwargs):


class InteractiveFigure(MplBaseFig, VBox):
    """
    Create an interactive Matplotlib figure.
    """

    def __init__(self, View, *args, **kwargs):
        from ...widgets import HBar, VBar, make_toolbar_canvas2d

        self.__init_figure__(View, *args, **kwargs)
        self.toolbar = make_toolbar_canvas2d(
            home=self._view.autoscale,
            canvas=self._view.canvas,
            colormapper=getattr(self._view, 'colormapper', None),
        )
        self.left_bar = VBar([self.toolbar])
        self.right_bar = VBar()
        self.bottom_bar = HBar()
        self.top_bar = HBar()

        super().__init__(
            [
                self.top_bar,
                HBar([self.left_bar, self._view.canvas.to_widget(), self.right_bar]),
                self.bottom_bar,
            ]
        )


class StaticFigure(MplBaseFig):
    """
    Create a static Matplotlib figure.
    The output will be either svg or png, depending on the number of drawn onto the
    canvas.
    """

    def __init__(self, View, *args, **kwargs):
        self.__init_figure__(View, *args, **kwargs)

    def _repr_mimebundle_(self, include=None, exclude=None) -> dict:
        """
        Mimebundle display representation for jupyter notebooks.
        """
        str_repr = str(self.fig)
        out = {'text/plain': str_repr[:-1] + f', {len(self.artists)} artists)'}
        if self._view._repr_format is not None:
            repr_maker = get_repr_maker(form=self._view._repr_format)
        else:
            npoints = sum(len(line.get_xdata()) for line in self._view.canvas.ax.lines)
            repr_maker = get_repr_maker(npoints=npoints)
        out.update(repr_maker(self._view.canvas.fig))
        return out

    def to_widget(self):
        """
        Convert the Matplotlib figure to an image widget.
        """
        return self._view.canvas.to_image()


def Figure(*args, **kwargs):
    from .utils import is_interactive_backend

    if is_interactive_backend():
        return InteractiveFigure(*args, **kwargs)
    else:
        return StaticFigure(*args, **kwargs)
