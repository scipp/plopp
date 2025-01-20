# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)


from ..core import View


class BaseFig:
    """
    A Mixin class which is the base for all figures.
    """

    view: View

    @property
    def canvas(self):
        return self.view.canvas

    def autoscale(self):
        self.view.autoscale()

    @property
    def artists(self):
        return self.view.artists

    @property
    def dims(self):
        return self.view.dims

    @property
    def graph_nodes(self):
        return self.view.graph_nodes

    @property
    def id(self):
        return self.view.id

    def update(self, *args, **kwargs):
        return self.view.update(*args, **kwargs)

    def notify_view(self, *args, **kwargs):
        return self.view.notify_view(*args, **kwargs)
