# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)
from __future__ import annotations

from ipywidgets import HBox, VBox
from matplotlib.axes import Axes
from matplotlib.figure import Figure as MplFigure

from ...graphics import BaseFig
from .canvas import Canvas
from .utils import fig_to_bytes, is_interactive_backend


class Figure(BaseFig, VBox):
    """
    Create a Matplotgl figure.
    """

    def __init__(self, View, *args, **kwargs):
        from ...widgets import HBar, VBar, make_toolbar_canvas2d

        self.interactive = True
        self.view = View(*args, **kwargs)
        self.toolbar = make_toolbar_canvas2d(view=self.view)
        self.left_bar = VBar([self.toolbar])
        self.right_bar = VBar()
        self.bottom_bar = HBar()
        self.top_bar = HBar()
        super().__init__(
            [
                self.top_bar,
                HBox([self.left_bar, self.view.canvas.to_widget(), self.right_bar]),
                self.bottom_bar,
            ]
        )

    def save(self, filename: str, **kwargs):
        """
        Save the figure to file.
        The default directory for writing the file is the same as the
        directory where the script or notebook is running.

        Parameters
        ----------
        filename:
            Name of the output file. Possible file extensions are ``.jpg``, ``.png``,
            ``.svg``, and ``.pdf``.
        """
        return self.view.canvas.save(filename, **kwargs)
