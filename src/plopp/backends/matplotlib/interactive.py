# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from ipywidgets import HBox, VBox

from ...widgets import HBar, VBar, make_toolbar_canvas2d
from .figure import Figure


class InteractiveFig(Figure, VBox):
    """
    Create an interactive Matplotlib figure.
    """

    def __init__(self, View, *args, **kwargs):
        self.__init_figure__(View, *args, **kwargs)
        self.toolbar = make_toolbar_canvas2d(
            canvas=self._view.canvas,
            colormapper=getattr(self._view, 'colormapper', None),
        )
        self.left_bar = VBar([self.toolbar])
        self.right_bar = VBar()
        self.bottom_bar = HBar()
        self.top_bar = HBar()

        super().__init__(
            [
                self.top_bar,
                HBox([self.left_bar, self._view.canvas.to_widget(), self.right_bar]),
                self.bottom_bar,
            ]
        )
