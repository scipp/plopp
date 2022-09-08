# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .displayable import Displayable
from .figure import Figure
from .toolbar import Toolbar

import ipywidgets as ipw


class SideBar(list, Displayable):

    def to_widget(self):
        return ipw.VBox([child.to_widget() for child in self])


class InteractiveFig(Figure):

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

    def _repr_mimebundle_(self, include=None, exclude=None):
        """
        Mimebundle display representation for jupyter notebooks.
        """
        return self.to_widget()._repr_mimebundle_(include=include, exclude=exclude)

    def to_widget(self) -> ipw.Widget:
        """
        Convert the Matplotlib figure to a widget.
        """
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
        if self._fig.canvas.toolbar.mode == "Zoom":
            self.toolbar.zoom()
        self._fig.canvas.toolbar.pan()

    def zoom(self):
        self._fig.canvas.toolbar.zoom()

    def save(self):
        self._fig.canvas.toolbar.save_figure()

    def logx(self):
        super().logx()
        self.toolbar.logx.value = self._ax.get_xscale() == 'log'

    def logy(self):
        super().logy()
        self.toolbar.logy.value = self._ax.get_yscale() == 'log'
