# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from ...graphics import BaseFig


class Figure(BaseFig):
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
