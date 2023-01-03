# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ...widgets import Toolbar, HBar, VBar, tools
from ...widgets.common import is_sphinx_build

from ipywidgets import VBox, HBox


class InteractiveFig1d(VBox):
    """
    Create an interactive figure to represent one-dimensional data.
    """

    def __init__(self, *args, FigConstructor, **kwargs):

        self._fig = FigConstructor(*args, **kwargs)
        self.toolbar = Toolbar(
            tools={
                'home':
                tools.HomeTool(self._fig.canvas.autoscale),
                'panzoom':
                tools.PanZoomTool(canvas=self._fig.canvas),
                'logx':
                tools.LogxTool(self._fig.canvas.logx,
                               value=self._fig.canvas.xscale == 'log'),
                'logy':
                tools.LogyTool(self._fig.canvas.logy,
                               value=self._fig.canvas.yscale == 'log'),
                'save':
                tools.SaveTool(self._fig.canvas.save_figure)
            })

        self.left_bar = VBar([self.toolbar])
        self.right_bar = VBar()
        self.bottom_bar = HBar()
        self.top_bar = HBar()

        super().__init__([
            self.top_bar,
            HBox([
                self.left_bar,
                self._fig.canvas.to_image()
                if is_sphinx_build() else self._fig.canvas.to_widget(), self.right_bar
            ]), self.bottom_bar
        ])

    @property
    def fig(self):
        return self._fig.canvas.fig

    @property
    def ax(self):
        return self._fig.canvas.ax

    @property
    def canvas(self):
        return self._fig.canvas

    @property
    def artists(self):
        return self._fig.artists

    @property
    def graph_nodes(self):
        return self._fig.graph_nodes

    def crop(self, *args, **kwargs):
        return self._fig.crop(*args, **kwargs)

    def save(self, *args, **kwargs):
        return self._fig.save(*args, **kwargs)

    def update(self, *args, **kwargs):
        return self._fig.update(*args, **kwargs)


class InteractiveFig2d(VBox):
    """
    Create an interactive figure to represent two-dimensional data.
    """

    def __init__(self, *args, FigConstructor, **kwargs):

        self._fig = FigConstructor(*args, **kwargs)
        self.toolbar = Toolbar(
            tools={
                'home':
                tools.HomeTool(self._fig.canvas.autoscale),
                'panzoom':
                tools.PanZoomTool(canvas=self._fig.canvas),
                'logx':
                tools.LogxTool(self._fig.canvas.logx,
                               value=self._fig.canvas.xscale == 'log'),
                'logy':
                tools.LogyTool(self._fig.canvas.logy,
                               value=self._fig.canvas.yscale == 'log'),
                'lognorm':
                tools.LogNormTool(self._fig.toggle_norm,
                                  value=self._fig.colormapper.norm == 'log'),
                'save':
                tools.SaveTool(self._fig.canvas.save_figure)
            })

        self.left_bar = VBar([self.toolbar])
        self.right_bar = VBar()
        self.bottom_bar = HBar()
        self.top_bar = HBar()

        super().__init__([
            self.top_bar,
            HBox([
                self.left_bar,
                self._fig.canvas.to_image()
                if is_sphinx_build() else self._fig.canvas.to_widget(), self.right_bar
            ]), self.bottom_bar
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
    def graph_nodes(self):
        return self._fig.graph_nodes

    def crop(self, *args, **kwargs):
        return self._fig.crop(*args, **kwargs)

    def save(self, *args, **kwargs):
        return self._fig.save(*args, **kwargs)

    def update(self, *args, **kwargs):
        return self._fig.update(*args, **kwargs)
