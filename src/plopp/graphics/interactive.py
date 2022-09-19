# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .fig import Figure
from .toolbar import Toolbar

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


class InteractiveFig(Figure, VBox):

    def __init__(self, *args, **kwargs):

        Figure.__init__(self, *args, **kwargs)
        VBox.__init__(self, [
            self.top_bar,
            HBox([
                self.left_bar,
                self._to_image() if _is_sphinx_build() else self._fig.canvas,
                self.right_bar
            ]), self.bottom_bar
        ])

    def _post_init(self):

        self._fig.canvas.toolbar_visible = False
        self._fig.canvas.header_visible = False

        self.left_bar = VBox()
        self.right_bar = VBox()
        self.bottom_bar = HBox()
        self.top_bar = HBox()

        self.toolbar = Toolbar(
            tools={
                'home': self.home,
                'pan': self.pan,
                'zoom': self.zoom,
                'logx': self.logx,
                'logy': self.logy,
                'save': self.save
            })
        self._fig.canvas.toolbar_visible = False
        self._fig.canvas.header_visible = False
        self.left_bar.children = tuple([self.toolbar])

    def home(self):
        self._autoscale()
        self.crop(**self._crop)
        self.draw()

    def pan(self):
        if self._fig.canvas.toolbar.mode == 'zoom rect':
            self.toolbar.zoom()
        self._fig.canvas.toolbar.pan()

    def zoom(self):
        if self._fig.canvas.toolbar.mode == 'pan/zoom':
            self.toolbar.pan()
        self._fig.canvas.toolbar.zoom()

    def save(self):
        self._fig.canvas.toolbar.save_figure()

    def logx(self):
        super().logx()
        self.toolbar.logx.value = self._ax.get_xscale() == 'log'

    def logy(self):
        super().logy()
        self.toolbar.logy.value = self._ax.get_yscale() == 'log'
