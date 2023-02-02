# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import os

from ipywidgets import HBox, VBox

from ...widgets import HBar, VBar, make_toolbar_canvas3d


class Figure(VBox):
    """
    Create a figure to represent three-dimensional data.
    """

    def __init__(self, *args, FigConstructor, **kwargs):

        self._fig = FigConstructor(*args, **kwargs)
        self.toolbar = make_toolbar_canvas3d(canvas=self._fig.canvas,
                                             colormapper=self._fig.colormapper)
        self.left_bar = VBar([self.toolbar])
        self.right_bar = VBar([self._fig.colormapper.to_widget()])
        self.bottom_bar = HBar()
        self.top_bar = HBar()

        super().__init__([
            self.top_bar,
            HBox([self.left_bar,
                  self._fig.canvas.to_widget(), self.right_bar]), self.bottom_bar
        ])

    @property
    def canvas(self):
        return self._fig.canvas

    @property
    def artists(self):
        return self._fig.artists

    @property
    def dims(self):
        return self._fig.dims

    @property
    def graph_nodes(self):
        return self._fig.graph_nodes

    @property
    def id(self):
        return self._fig.id

    def update(self, *args, **kwargs):
        return self._fig.update(*args, **kwargs)

    def notify_view(self, *args, **kwargs):
        return self._fig.notify_view(*args, **kwargs)

    def get_limits(self, *args, **kwargs):
        return self._fig.get_limits(*args, **kwargs)

    def set_opacity(self, *args, **kwargs):
        return self._fig.set_opacity(*args, **kwargs)

    def remove(self, *args, **kwargs):
        return self._fig.remove(*args, **kwargs)

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
        out = HBox([self._fig.canvas.to_widget(), self.right_bar])
        # Garbage collection for embedded html output:
        # https://github.com/jupyter-widgets/pythreejs/issues/217
        state = dependency_state(out)
        # convert and write to file
        embed_minimal_html(
            filename,
            out,
            title=self._fig.canvas.title if self._fig.canvas.title else 'figure3d',
            state=state)
