# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ...graphics.fig1d import Figure1d
from ...graphics.fig2d import Figure2d
from ...graphics.fig3d import Figure3d
from ...widgets import Toolbar, HBar, VBar, tools
# from ...widgets.common import is_sphinx_build

from ipywidgets import VBox, HBox


class Fig1d(VBox):
    """
    Create an interactive figure to represent one-dimensional data.
    """

    def __init__(self, *args, **kwargs):

        self._fig = Figure1d(*args, **kwargs)
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
            HBox([self.left_bar, self._fig.canvas.fig, self.right_bar]), self.bottom_bar
        ])

    def __getattr__(self, key):
        try:
            return getattr(super(), key)
        except AttributeError:
            return getattr(self._fig, key)

    def __dir__(self):
        return list(set(dir(VBox) + dir(super()) + dir(self._fig)))


class Fig2d(VBox):
    """
    Create an interactive figure to represent two-dimensional data.
    """

    def __init__(self, *args, **kwargs):

        self._fig = Figure2d(*args, **kwargs)
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
            HBox([self.left_bar, self._fig.canvas.fig, self.right_bar]), self.bottom_bar
        ])

    def __getattr__(self, key):
        try:
            return getattr(super(), key)
        except AttributeError:
            return getattr(self._fig, key)

    def __dir__(self):
        return list(set(dir(VBox) + dir(super()) + dir(self._fig)))


def figure1d(*args, **kwargs):
    """
    Make a 1d figure that is either static or interactive depending on the backend in
    use.
    """
    return Fig1d(*args, **kwargs)


def figure2d(*args, **kwargs):
    """
    Make a 2d figure that is either static or interactive depending on the backend in
    use.
    """
    return Fig2d(*args, **kwargs)


# def figure3d(*args, **kwargs):
#     """
#     Make a 3d figure.
#     """
#     from .interactive import InteractiveFig3d
#     return InteractiveFig3d(*args, **kwargs)
