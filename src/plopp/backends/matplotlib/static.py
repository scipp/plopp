# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from .utils import copy_figure, fig_to_bytes


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


class StaticFig:
    """
    Create a static figure to represent one-dimensional data.
    """

    def __init__(self, *args, FigConstructor, **kwargs):
        self._fig = FigConstructor(*args, **kwargs)
        self._args = args
        self._kwargs = kwargs
        self._fig_constructor = FigConstructor

    def _repr_mimebundle_(self, include=None, exclude=None) -> dict:
        """
        Mimebundle display representation for jupyter notebooks.
        """
        str_repr = str(self.fig)
        out = {'text/plain': str_repr[:-1] + f', {len(self.artists)} artists)'}
        if self._fig._repr_format is not None:
            repr_maker = get_repr_maker(form=self._fig._repr_format)
        else:
            npoints = sum(len(line.get_xdata()) for line in self._fig.canvas.ax.lines)
            repr_maker = get_repr_maker(npoints=npoints)
        out.update(repr_maker(self._fig.canvas.fig))
        return out

    def copy(self, **kwargs):
        return copy_figure(fig=self, **kwargs)

    def to_widget(self):
        """
        Convert the Matplotlib figure to an image widget.
        """
        return self._fig.canvas.to_image()

    @property
    def fig(self):
        """
        Get the underlying Matplotlib figure.
        """
        return self._fig.canvas.fig

    @property
    def ax(self):
        """
        Get the underlying Matplotlib axes.
        """
        return self._fig.canvas.ax

    @property
    def cax(self):
        """
        Get the underlying Matplotlib colorbar axes.
        """
        return self._fig.canvas.cax

    @property
    def canvas(self):
        return self._fig.canvas

    @property
    def artists(self):
        return self._fig.artists

    @property
    def graph_nodes(self):
        return self._fig.graph_nodes

    @property
    def id(self):
        return self._fig.id

    def crop(self, **limits):
        """
        Set the axes limits according to the crop parameters.

        Parameters
        ----------
        **limits:
            Min and max limits for each dimension to be cropped.
        """
        return self._fig.crop(**limits)

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
        return self._fig.canvas.save(filename, **kwargs)

    def update(self, *args, **kwargs):
        return self._fig.update(*args, **kwargs)

    def notify_view(self, *args, **kwargs):
        return self._fig.notify_view(*args, **kwargs)

    def __add__(self, other):
        from .tiled import hstack

        return hstack(self, other)

    def __truediv__(self, other):
        from .tiled import vstack

        return vstack(self, other)
