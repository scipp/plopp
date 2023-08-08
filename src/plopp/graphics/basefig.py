# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)


from ..core import View


class BaseFig:
    """
    A Mixin class which is the base for all figures.
    """

    _view: View

    @property
    def canvas(self):
        return self._view.canvas

    @property
    def artists(self):
        return self._view.artists

    @property
    def graph_nodes(self):
        return self._view.graph_nodes

    @property
    def id(self):
        return self._view.id

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

    def update(self, *args, **kwargs):
        return self._view.update(*args, **kwargs)

    def notify_view(self, *args, **kwargs):
        return self._view.notify_view(*args, **kwargs)
