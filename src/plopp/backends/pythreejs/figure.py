# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ...widgets import Toolbar, HBar, VBar, tools
from ipywidgets import VBox, HBox


class Fig3d(VBox):
    """
    Create a figure to represent three-dimensional data.
    """

    def __init__(self, *args, FigConstructor, **kwargs):

        self._fig = FigConstructor(*args, **kwargs)
        self.toolbar = Toolbar(
            tools={
                'home':
                tools.HomeTool(self._fig.canvas.home),
                'camerax':
                tools.CameraTool(self._fig.canvas.camera_x_normal,
                                 description='X',
                                 tooltip='Camera to X normal. '
                                 'Click twice to flip the view direction.'),
                'cameray':
                tools.CameraTool(self._fig.canvas.camera_y_normal,
                                 description='Y',
                                 tooltip='Camera to Y normal. '
                                 'Click twice to flip the view direction.'),
                'cameraz':
                tools.CameraTool(self._fig.canvas.camera_z_normal,
                                 description='Z',
                                 tooltip='Camera to Z normal. '
                                 'Click twice to flip the view direction.'),
                'lognorm':
                tools.LogNormTool(self._fig.colormapper.toggle_norm,
                                  value=self._fig.colormapper.norm == 'log'),
                'box':
                tools.OutlineTool(self._fig.canvas.toggle_outline),
                'axes':
                tools.AxesTool(self._fig.canvas.toggle_axes3d)
            })

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
