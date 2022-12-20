# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ...graphics.fig1d import Figure1d
from ...graphics.fig2d import Figure2d
from .utils import fig_to_bytes


def _make_png_repr(fig):
    return {'image/png': fig_to_bytes(fig, form='png')}


def _make_svg_repr(fig):
    return {'image/svg+xml': fig_to_bytes(fig, form='svg').decode()}


REPR_MAP = {'png': _make_png_repr, 'svg': _make_svg_repr}

# def _make_mimebundle_(obj) -> dict:
#     """
#     Mimebundle display representation for jupyter notebooks.
#     """
#     out = {'text/plain': 'Figure'}
#     if obj._repr_format is not None:
#         repr_maker = REPR_MAP[obj._repr_format.lower()]
#     else:
#         npoints = 0
#         for line in obj.canvas.ax.lines:
#             npoints += len(line.get_xdata())
#         repr_maker = REPR_MAP['png' if (npoints > 20_000) else 'svg']
#     out.update(repr_maker(obj.canvas.fig))
#     return out

# class Static:
#     """
#     Mixin class to provide the svg repr for static figures, as well as a method to
#     convert them to a widget.
#     """

#     def _repr_mimebundle_(self, include=None, exclude=None) -> dict:
#         """
#         Mimebundle display representation for jupyter notebooks.
#         """
#         return _make_mimebundle_(obj=self)
#         out = {'text/plain': 'Figure'}
#         if self._repr_format is not None:
#             repr_maker = REPR_MAP[self._repr_format.lower()]
#         else:
#             npoints = 0
#             for line in self.canvas.ax.lines:
#                 npoints += len(line.get_xdata())
#             repr_maker = REPR_MAP['png' if (npoints > 20_000) else 'svg']
#         out.update(repr_maker(self.canvas.fig))
#         return out

#     def to_widget(self):
#         """
#         Convert the Matplotlib figure to an image widget.
#         """
#         return self.canvas.to_image()


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


# class StaticFig1d:
#     """
#     Create a static figure to represent one-dimensional data.
#     """

#     def __init__(self, *args, FigConstructor, **kwargs):

#         self._fig = FigConstructor(*args, **kwargs)

#     def __getattr__(self, key):
#         return getattr(self._fig, key)

#     def __dir__(self):
#         return dir(self._fig)

#     def _repr_mimebundle_(self, include=None, exclude=None) -> dict:
#         """
#         Mimebundle display representation for jupyter notebooks.
#         """

#     def to_widget(self):
#         """
#         Convert the Matplotlib figure to an image widget.
#         """
#         return self.canvas.to_image()

# # class StaticFig2d(Static, Figure2d):
# #     """
# #     Create a static figure to represent two-dimensional data.
# #     """
# #     pass
