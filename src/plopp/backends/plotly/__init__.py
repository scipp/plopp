# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)


class PlotlyBackend:

    def is_interactive(self):
        """
        Returns ``True`` if the backend currently in use allows for interactive figures.
        """
        return True

    def canvas2d(self, *args, **kwargs):
        """
        See :class:`canvas.Canvas` for details.
        """
        from .canvas import Canvas as CanvasPlotly
        return CanvasPlotly(*args, **kwargs)

    def line(self, *args, **kwargs):
        """
        See :class:`line.Line` for details.
        """
        from .line import Line as LinePlotly
        return LinePlotly(*args, **kwargs)

    def figure1d(self, *args, **kwargs):
        """
        See :class:`figure.Figure` for details.
        """
        from .figure import Figure as FigPlotly
        return FigPlotly(*args, **kwargs)
