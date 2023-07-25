# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from ...graphics import BaseFig


class Figure(BaseFig):  # Should this be named a Plot?
    """
    Mixin class for Matplotlib figures
    """

    def __init_figure__(self, View, *args, **kwargs):
        self._view = View(*args, **kwargs)
        self._args = args
        self._kwargs = kwargs
        # self._v_constructor = View

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

    # @property
    # def canvas(self):
    #     return self._view.canvas

    # @property
    # def artists(self):
    #     return self._view.artists

    # @property
    # def graph_nodes(self):
    #     return self._view.graph_nodes

    # @property
    # def id(self):
    #     return self._view.id

    # def crop(self, **limits):
    #     """
    #     Set the axes limits according to the crop parameters.

    #     Parameters
    #     ----------
    #     **limits:
    #         Min and max limits for each dimension to be cropped.
    #     """
    #     return self._view.crop(**limits)

    # def save(self, filename, **kwargs):
    #     """
    #     Save the figure to file.
    #     The default directory for writing the file is the same as the
    #     directory where the script or notebook is running.

    #     Parameters
    #     ----------
    #     filename:
    #         Name of the output file. Possible file extensions are ``.jpg``, ``.png``,
    #         ``.svg``, and ``.pdf``.
    #     """
    #     return self._view.canvas.save(filename, **kwargs)

    # def update(self, *args, **kwargs):
    #     return self._view.update(*args, **kwargs)

    # def notify_view(self, *args, **kwargs):
    #     return self._view.notify_view(*args, **kwargs)

    def __add__(self, other):
        from .tiled import hstack

        return hstack(self, other)

    def __truediv__(self, other):
        from .tiled import vstack

        return vstack(self, other)
