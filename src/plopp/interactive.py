# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .displayable import Displayable
from .figure import Figure
from .toolbar import Toolbar

import ipywidgets as ipw


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
    if not running_in_jupyter():
        return False
    from IPython import get_ipython
    ipy = get_ipython()
    cfg = ipy.config
    meta = cfg["Session"]["metadata"]
    if hasattr(meta, "to_dict"):
        meta = meta.to_dict()
    return meta.get("scipp_sphinx_build", False)


class SideBar(list, Displayable):

    def to_widget(self):
        return ipw.VBox([child.to_widget() for child in self])


class InteractiveFig(Figure, Displayable):

    def _post_init(self):

        self._fig.canvas.toolbar_visible = False
        self._fig.canvas.header_visible = False

        self.left_bar = SideBar()
        self.right_bar = SideBar()
        self.bottom_bar = SideBar()
        self.top_bar = SideBar()

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
        self.left_bar.append(self.toolbar)

    def to_widget(self) -> ipw.Widget:
        """
        Convert the Matplotlib figure to a widget.
        """
        if self.is_widget() and (not is_sphinx_build()):
            return ipw.HBox([self.toolbar._to_widget(), self.fig.canvas])
        else:
            return self._to_image()

        return ipw.VBox([
            self.top_bar.to_widget(),
            ipw.HBox([
                self.left_bar.to_widget(), self._fig.canvas,
                self.right_bar.to_widget()
            ]),
            self.bottom_bar.to_widget()
        ])

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
