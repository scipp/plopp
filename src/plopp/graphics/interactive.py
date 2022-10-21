# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .fig1d import Figure1d
from .fig2d import Figure2d
from .fig3d import Figure3d
from ..widgets import Toolbar, HBar, VBar, tools

from ipywidgets import VBox, HBox


def _running_in_jupyter() -> bool:
    """
    Detect whether Python is running in Jupyter.

    Note that this includes not only Jupyter notebooks
    but also Jupyter console and qtconsole.
    """
    try:
        from IPython import get_ipython
        import ipykernel.zmqshell
    except ImportError:
        # Cannot be Jupyter if IPython is not installed.
        return False

    return isinstance(get_ipython(), ipykernel.zmqshell.ZMQInteractiveShell)


def _is_sphinx_build():
    """
    Returns `True` if we are running inside a sphinx documentation build.
    """
    if not _running_in_jupyter():
        return False
    from IPython import get_ipython
    ipy = get_ipython()
    cfg = ipy.config
    meta = cfg["Session"]["metadata"]
    if hasattr(meta, "to_dict"):
        meta = meta.to_dict()
    return meta.get("scipp_sphinx_build", False)


class InteractiveFig1d(VBox):

    def __init__(self, *args, **kwargs):

        self._fig = Figure1d(*args, **kwargs)
        self.toolbar = Toolbar(
            tools={
                'home': tools.HomeTool(self._fig.canvas.autoscale),
                'panzoom': tools.PanZoomTool(canvas=self._fig.canvas),
                'logx': tools.LogxTool(self._fig.canvas.logx),
                'logy': tools.LogyTool(self._fig.canvas.logy),
                'save': tools.SaveTool(self._fig.canvas.save)
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
                if _is_sphinx_build() else self._fig.canvas.fig.canvas, self.right_bar
            ]), self.bottom_bar
        ])

    def __getattr__(self, key):
        try:
            return getattr(super(), key)
        except AttributeError:
            return getattr(self._fig, key)

    def __dir__(self):
        return list(set(dir(VBox) + dir(super()) + dir(self._fig)))


class InteractiveFig2d(VBox):

    def __init__(self, *args, **kwargs):

        self._fig = Figure2d(*args, **kwargs)
        self.toolbar = Toolbar(
            tools={
                'home': tools.HomeTool(self._fig.canvas.autoscale),
                'panzoom': tools.PanZoomTool(canvas=self._fig.canvas),
                'logx': tools.LogxTool(self._fig.canvas.logx),
                'logy': tools.LogyTool(self._fig.canvas.logy),
                'lognorm': tools.LogNormTool(self._fig.toggle_norm),
                'save': tools.SaveTool(self._fig.canvas.save)
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
                if _is_sphinx_build() else self._fig.canvas.fig.canvas, self.right_bar
            ]), self.bottom_bar
        ])

    def __getattr__(self, key):
        try:
            return getattr(super(), key)
        except AttributeError:
            return getattr(self._fig, key)

    def __dir__(self):
        return list(set(dir(VBox) + dir(super()) + dir(self._fig)))


class InteractiveFig3d(VBox):

    def __init__(self, *args, **kwargs):

        self._fig = Figure3d(*args, **kwargs)
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
                tools.CameraTool(self._fig.canvas.camera_y_normal,
                                 description='Z',
                                 tooltip='Camera to Z normal. '
                                 'Click twice to flip the view direction.'),
                'lognorm':
                tools.LogNormTool(self._fig.colormapper.toggle_norm),
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
            HBox([self.left_bar, self._fig.canvas.renderer, self.right_bar]),
            self.bottom_bar
        ])

    def __getattr__(self, key):
        try:
            return getattr(super(), key)
        except AttributeError:
            return getattr(self._fig, key)

    def __dir__(self):
        return list(set(dir(VBox) + dir(super()) + dir(self._fig)))
