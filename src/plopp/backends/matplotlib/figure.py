# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)


class Figure:
    """
    Mixin class for Matplotlib figures
    """

    def __init_figure__(self, FigConstructor, *args, **kwargs):
        self._fig = FigConstructor(*args, **kwargs)
        self._args = args
        self._kwargs = kwargs
        self._fig_constructor = FigConstructor

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
