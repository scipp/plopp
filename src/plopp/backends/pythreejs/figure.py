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
        self._view = View(*args, **kwargs)
        self.toolbar = make_toolbar_canvas3d(
            canvas=self._view.canvas, colormapper=self._view.colormapper
        )
        self.left_bar = VBar([self.toolbar])
        self.right_bar = VBar([self._view.colormapper.to_widget()])
        self.bottom_bar = HBar()
        self.top_bar = HBar([self._view.canvas._title])

        super().__init__(
            [
                self.top_bar,
                HBox([self.left_bar, self._view.canvas.to_widget(), self.right_bar]),
                self.bottom_bar,
            ]
        )

    # @property
    # def canvas(self):
    #     return self._view.canvas

    # @property
    # def artists(self):
    #     return self._view.artists

    # @property
    # def dims(self):
    #     return self._view.dims

    # @property
    # def graph_nodes(self):
    #     return self._view.graph_nodes

    # @property
    # def id(self):
    #     return self._view.id

    # def update(self, *args, **kwargs):
    #     return self._view.update(*args, **kwargs)

    # def notify_view(self, *args, **kwargs):
    #     return self._view.notify_view(*args, **kwargs)

    # def get_limits(self, *args, **kwargs):
    #     return self._view.get_limits(*args, **kwargs)

    # def set_opacity(self, *args, **kwargs):
    #     return self._view.set_opacity(*args, **kwargs)

    # def remove(self, *args, **kwargs):
    #     return self._view.remove(*args, **kwargs)

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

        out = HBox([self._view.canvas.to_widget(), self.right_bar])
        # Garbage collection for embedded html output:
        # https://github.com/jupyter-widgets/pythreejs/issues/217
        state = dependency_state(out)
        # convert and write to file
        embed_minimal_html(
            filename,
            out,
            title=self._view.canvas.title if self._view.canvas.title else 'figure3d',
            state=state,
        )
