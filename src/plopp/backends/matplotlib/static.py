# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from .figure import Figure
from .utils import fig_to_bytes


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


class StaticFig(Figure):
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
