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

    # @property
    # def ax(self):
    #     return self._view.canvas.ax

    def autoscale(self):
        self._view.autoscale()

    @property
    def artists(self):
        return self._view.artists

    @property
    def dims(self):
        return self._view.dims

    @property
    def graph_nodes(self):
        return self._view.graph_nodes

    @property
    def id(self):
        return self._view.id

    def update(self, *args, **kwargs):
        return self._view.update(*args, **kwargs)

    def notify_view(self, *args, **kwargs):
        return self._view.notify_view(*args, **kwargs)
