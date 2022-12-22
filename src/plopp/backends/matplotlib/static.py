# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .utils import fig_to_bytes


def _make_png_repr(fig):
    return {'image/png': fig_to_bytes(fig, form='png')}


def _make_svg_repr(fig):
    return {'image/svg+xml': fig_to_bytes(fig, form='svg').decode()}


REPR_MAP = {'png': _make_png_repr, 'svg': _make_svg_repr}


class StaticFig:
    """
    Create a static figure to represent one-dimensional data.
    """

    def __init__(self, *args, FigConstructor, **kwargs):

        self._fig = FigConstructor(*args, **kwargs)

    def __getattr__(self, key):
        return getattr(self._fig, key)

    def __dir__(self):
        return dir(self._fig)

    def _repr_mimebundle_(self, include=None, exclude=None) -> dict:
        """
        Mimebundle display representation for jupyter notebooks.
        """
        out = {'text/plain': 'Figure'}
        if self._fig._repr_format is not None:
            repr_maker = REPR_MAP[self._fig._repr_format.lower()]
        else:
            npoints = 0
            for line in self._fig.canvas.ax.lines:
                npoints += len(line.get_xdata())
            repr_maker = REPR_MAP['png' if (npoints > 20_000) else 'svg']
        out.update(repr_maker(self._fig.canvas.fig))
        return out

    def to_widget(self):
        """
        Convert the Matplotlib figure to an image widget.
        """
        return self._fig.canvas.to_image()
