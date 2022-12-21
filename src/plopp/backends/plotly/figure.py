# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ...widgets import Toolbar, HBar, VBar, tools
# from ...widgets.common import is_sphinx_build

from ipywidgets import VBox, HBox


class Fig1d(VBox):
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
            HBox([self.left_bar,
                  self._fig.canvas.to_widget(), self.right_bar]), self.bottom_bar
        ])

    def __getattr__(self, key):
        try:
            return getattr(super(), key)
        except AttributeError:
            return getattr(self._fig, key)

    def __dir__(self):
        return list(set(dir(VBox) + dir(super()) + dir(self._fig)))
