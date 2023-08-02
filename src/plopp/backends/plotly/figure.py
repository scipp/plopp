# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from ipywidgets import HBox, VBox

from ...widgets import HBar, VBar, make_toolbar_canvas2d


class Figure(VBox):
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

    @property
    def canvas(self):
        return self._fig.canvas

    @property
    def artists(self):
        return self._fig.artists

    @property
    def graph_nodes(self):
        return self._fig.graph_nodes

    @property
    def id(self):
        return self._fig.id

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
        return self._fig.canvas.save(filename, **kwargs)

    def update(self, *args, **kwargs):
        return self._fig.update(*args, **kwargs)

    def notify_view(self, *args, **kwargs):
        return self._fig.notify_view(*args, **kwargs)
