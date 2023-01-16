# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from ipywidgets import HBox, VBox

from ...widgets import HBar, VBar, make_toolbar_canvas2d


class InteractiveFig(VBox):
    """
    Create an interactive figure.
    """

    def __init__(self, *args, FigConstructor, **kwargs):

        self._fig = FigConstructor(*args, **kwargs)
        self.toolbar = make_toolbar_canvas2d(canvas=self._fig.canvas,
                                             colormapper=getattr(
                                                 self._fig, 'colormapper', None))
        self.left_bar = VBar([self.toolbar])
        self.right_bar = VBar()
        self.bottom_bar = HBar()
        self.top_bar = HBar()

        super().__init__([
            self.top_bar,
            HBox([self.left_bar,
                  self._fig.canvas.to_widget(), self.right_bar]), self.bottom_bar
        ])

    @property
    def fig(self):
        """
        Get the underlying Matplotlib figure.
        """
        return self._fig.canvas.fig

    @property
    def ax(self):
        """
        Get the underlying Matplotlib axes.
        """
        return self._fig.canvas.ax

    @property
    def cax(self):
        """
        Get the underlying Matplotlib colorbar axes.
        """
        return self._fig.canvas.cax

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

    def crop(self, **limits):
        """
        Set the axes limits according to the crop parameters.

        Parameters
        ----------
        **limits:
            Min and max limits for each dimension to be cropped.
        """
        return self._fig.crop(**limits)

    def save(self, filename, **kwargs):
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
        return self._fig.canvas.save(filename, **kwargs)

    def update(self, *args, **kwargs):
        return self._fig.update(*args, **kwargs)

    def notify_view(self, *args, **kwargs):
        return self._fig.notify_view(*args, **kwargs)
