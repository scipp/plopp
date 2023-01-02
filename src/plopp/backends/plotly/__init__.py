# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)


class PlotlyBackend:

    @property
    def is_interactive(self):
        return True

    @property
    def Canvas2d(self):
        from .canvas import Canvas as CanvasPlotly
        return CanvasPlotly

    @property
    def Line(self):
        from .line import Line as LinePlotly
        return LinePlotly

    @property
    def Fig1d(self):
        from .figure import Fig1d as Fig1dPlotly
        return Fig1dPlotly
