# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from ipywidgets import HBox, VBox

from ...graphics import BaseFig
from ...widgets import HBar, VBar, make_toolbar_canvas2d


class Figure(BaseFig, VBox):
    """
    Create an interactive figure to represent one-dimensional data.
    """

    def __init__(self, FigConstructor, *args, **kwargs):
        self._fig = FigConstructor(*args, **kwargs)
        self.toolbar = make_toolbar_canvas2d(canvas=self._fig.canvas)
        self.left_bar = VBar([self.toolbar])
        self.right_bar = VBar()
        self.bottom_bar = HBar()
        self.top_bar = HBar()

        super().__init__(
            [
                self.top_bar,
                HBox([self.left_bar, self._fig.canvas.to_widget(), self.right_bar]),
                self.bottom_bar,
            ]
        )
