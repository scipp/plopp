# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .fig1d import Figure1d
from .fig2d import Figure2d
from ..widgets import Toolbar, HBar, VBar

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


class Interactive(VBox):

    def __init__(self):

        # self.left_bar = VBox()
        # self.right_bar = VBox()
        # self.bottom_bar = HBox()
        # self.top_bar = HBox()

        self.toolbar = Toolbar(
            tools={
                'home': self.home,
                'pan': self.pan,
                'zoom': self.zoom,
                'logx': self.logx,
                'logy': self.logy,
                'save': self.save
            })

        # self._fig.canvas.toolbar_visible = False
        # self._fig.canvas.header_visible = False

        self.left_bar = VBar([self.toolbar])
        self.right_bar = VBar()
        self.bottom_bar = HBar()
        self.top_bar = HBar()

        # self.left_bar.children = tuple([self.toolbar])

        # self.figure = Figure.__init__(self, *args, **kwargs)

        super().__init__([
            self.top_bar,
            HBox([
                self.left_bar,
                # self._to_image() if _is_sphinx_build() else self._fig.canvas,
                self.figure.canvas.fig.canvas,
                self.right_bar
            ]),
            self.bottom_bar
        ])

    # def _post_init(self):

    #     self._fig.canvas.toolbar_visible = False
    #     self._fig.canvas.header_visible = False

    #     self.left_bar = VBox()
    #     self.right_bar = VBox()
    #     self.bottom_bar = HBox()
    #     self.top_bar = HBox()

    #     self.toolbar = Toolbar(
    #         tools={
    #             'home': self.home,
    #             'pan': self.pan,
    #             'zoom': self.zoom,
    #             'logx': self.logx,
    #             'logy': self.logy,
    #             'save': self.save
    #         })
    #     self._fig.canvas.toolbar_visible = False
    #     self._fig.canvas.header_visible = False
    #     self.left_bar.children = tuple([self.toolbar])

    def home(self):
        self.figure.canvas.autoscale()
        # self.figure.canvas.crop(**self._crop)
        self.figure.canvas.draw()

    def pan(self):
        if self.figure.canvas.toolbar_mode == 'zoom rect':
            self.toolbar.zoom()
        self.figure.canvas.pan()

    def zoom(self):
        if self.figure.canvas.toolbar_mode == 'pan/zoom':
            self.toolbar.pan()
        self.figure.canvas.zoom()

    def save(self):
        self.figure.canvas.save()

    def logx(self):
        # super().logx()
        self.figure.canvas.xscale = 'log' if self.toolbar.logx.value else 'linear'
        self.figure.autoscale()
        self.figure.canvas.draw()

    def logy(self):
        # super().logy()
        self.figure.canvas.yscale = 'log' if self.toolbar.logy.value else 'linear'
        self.figure.autoscale()
        self.figure.canvas.draw()
        # self.toolbar.logy.value = self._ax.get_yscale() == 'log'


class InteractiveFig1d(Interactive):

    def __init__(self, *args, **kwargs):
        self.figure = Figure1d(*args, **kwargs)
        self.figure.canvas.fig.canvas.toolbar_visible = False
        self.figure.canvas.fig.canvas.header_visible = False
        super().__init__()
        self.toolbar.logx.value = self.figure.canvas.xscale == 'log'
        self.toolbar.logy.value = self.figure.canvas.yscale == 'log'


class InteractiveFig2d(Interactive):

    def __init__(self, *args, **kwargs):
        self.figure = Figure2d(*args, **kwargs)
        self.figure.canvas.fig.canvas.toolbar_visible = False
        self.figure.canvas.fig.canvas.header_visible = False
        super().__init__()
        self.toolbar.logx.value = self.figure.canvas.xscale == 'log'
        self.toolbar.logy.value = self.figure.canvas.yscale == 'log'
