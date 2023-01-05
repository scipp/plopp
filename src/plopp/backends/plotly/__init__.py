# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)


class PlotlyBackend:

    def is_interactive(self):
        return True

    def canvas2d(self, *args, **kwargs):
        from .canvas import Canvas as CanvasPlotly
        return CanvasPlotly(*args, **kwargs)

    def line(self, *args, **kwargs):
        from .line import Line as LinePlotly
        return LinePlotly(*args, **kwargs)

    def figure1d(self, *args, **kwargs):
        from .figure import Figure as FigPlotly
        return FigPlotly(*args, **kwargs)
