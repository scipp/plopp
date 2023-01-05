# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ...widgets import HBar, VBar, make_toolbar_canvas3d
from ipywidgets import VBox, HBox


class Figure(VBox):
    """
    Create a figure to represent three-dimensional data.
    """

    def __init__(self, *args, FigConstructor, **kwargs):

        self._fig = FigConstructor(*args, **kwargs)
        self.toolbar = make_toolbar_canvas3d(canvas=self._fig.canvas,
                                             colormapper=self._fig.colormapper)
        self.left_bar = VBar([self.toolbar])
        self.right_bar = VBar([self._fig.colormapper.to_widget()])
        self.bottom_bar = HBar()
        self.top_bar = HBar()

        super().__init__([
            self.top_bar,
            HBox([self.left_bar,
                  self._fig.canvas.to_widget(), self.right_bar]), self.bottom_bar
        ])

    @property
    def canvas(self):
        return self._fig.canvas

    @property
    def artists(self):
        return self._fig.artists

    @property
    def dims(self):
        return self._fig.dims

    @property
    def graph_nodes(self):
        return self._fig.graph_nodes

    def update(self, *args, **kwargs):
        return self._fig.update(*args, **kwargs)

    def get_limits(self, *args, **kwargs):
        return self._fig.get_limits(*args, **kwargs)

    def set_opacity(self, *args, **kwargs):
        return self._fig.set_opacity(*args, **kwargs)

    def remove(self, *args, **kwargs):
        return self._fig.remove(*args, **kwargs)
