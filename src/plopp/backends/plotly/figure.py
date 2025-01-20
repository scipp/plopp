# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from ipywidgets import HBox, VBox

from ...graphics import BaseFig
from ...widgets import HBar, VBar, make_toolbar_canvas2d


class Figure(BaseFig, VBox):
    """
    Create an interactive figure to represent one-dimensional data.
    """

    def __init__(self, View, *args, **kwargs):
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

    def save(self, filename, **kwargs):
        """
        Save the figure to file.
        The default directory for writing the file is the same as the
        directory where the script or notebook is running.

        Parameters
        ----------
        filename:
            Name of the output file. Possible file extensions are ``.jpg``, ``.png``,
            ``.svg``, ``.pdf``, and ``html``.
        """
        return self.view.canvas.save(filename, **kwargs)
