# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import os

from ipywidgets import HBox, VBox

from ...graphics import BaseFig
from ...widgets import HBar, VBar, make_toolbar_canvas3d


class Figure(BaseFig, VBox):
    """
    Create a figure to represent three-dimensional data.
    """

    def __init__(self, View, *args, **kwargs):
        self.view = View(*args, **kwargs)
        self.toolbar = make_toolbar_canvas3d(view=self.view)
        self.left_bar = VBar([self.toolbar])
        self.right_bar = VBar(
            [self.view.colormapper.to_widget()]
            if self.view.colormapper is not None
            else []
        )
        self.bottom_bar = HBar()
        self.top_bar = HBar([self.view.canvas._title])

        super().__init__(
            [
                self.top_bar,
                HBox([self.left_bar, self.view.canvas.to_widget(), self.right_bar]),
                self.bottom_bar,
            ]
        )

    def save(self, filename):
        """
        Save the figure to a standalone HTML file.
        The default directory for writing the file is the same as the
        directory where the script or notebook is running.

        Parameters
        ----------
        filename:
            Name of the output HTML file.
        """
        ext = os.path.splitext(filename)[1]
        if ext.lower() != '.html':
            raise ValueError('File extension must be .html for saving 3d figures.')
        from ipywidgets.embed import dependency_state, embed_minimal_html

        out = HBox([self.view.canvas.to_widget(), self.right_bar])
        # Garbage collection for embedded html output:
        # https://github.com/jupyter-widgets/pythreejs/issues/217
        state = dependency_state(out)
        # convert and write to file
        embed_minimal_html(
            filename,
            out,
            title=self.view.canvas.title if self.view.canvas.title else 'figure3d',
            state=state,
        )
