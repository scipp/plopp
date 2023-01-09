# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from ...widgets import HBar, VBar, make_toolbar_canvas2d

from ipywidgets import VBox, HBox


class InteractiveFig(VBox):
    """
    Create an interactive figure.
    """

    def __init__(self, *args, FigConstructor, **kwargs):

        self._fig = FigConstructor(*args, **kwargs)
        self.toolbar = make_toolbar_canvas2d(canvas=self._fig.canvas,
                                             colormapper=getattr(
                                                 self._fig, 'colormapper', None))
        self.left_bar = VBar([self.toolbar])
        self.right_bar = VBar()
        self.bottom_bar = HBar()
        self.top_bar = HBar()

        super().__init__([
            self.top_bar,
            HBox([self.left_bar,
                  self._fig.canvas.to_widget(), self.right_bar]), self.bottom_bar
        ])

    @property
    def fig(self):
        return self._fig.canvas.fig

    @property
    def ax(self):
        return self._fig.canvas.ax

    @property
    def cax(self):
        return self.canvas.cax

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

    def crop(self, *args, **kwargs):
        return self._fig.crop(*args, **kwargs)

    def save(self, *args, **kwargs):
        return self._fig.save(*args, **kwargs)

    def update(self, *args, **kwargs):
        return self._fig.update(*args, **kwargs)
