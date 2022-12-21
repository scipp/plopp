# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)


class BackendManager(dict):

    def __init__(self, backends={'2d': 'matplotlib', '3d': 'pythreejs'}):
        super().__init__()
        self.update(backends)

    @property
    def Canvas2d(self):
        if self['2d'] == 'matplotlib':
            from .matplotlib import Canvas as CanvasMpl
            return CanvasMpl
        elif self['2d'] == 'plotly':
            from .plotly import Canvas as CanvasPlotly
            return CanvasPlotly
        raise ValueError(f'Unsupported backend {self["2d"]} for Canvas2d.')

    @property
    def Line(self):
        if self['2d'] == 'matplotlib':
            from .matplotlib import Line as LineMpl
            return LineMpl
        elif self['2d'] == 'plotly':
            from .plotly import Line as LinePlotly
            return LinePlotly
        raise ValueError(f'Unsupported backend {self["2d"]} for Line (1D).')

    @property
    def Image(self):
        if self.backend == 'matplotlib':
            from .matplotlib import Image as ImageMpl
            return ImageMpl
        raise ValueError(f'Unsupported backend {self["2d"]} for Image (2D).')

    @property
    def Fig1d(self):
        if self['2d'] == 'matplotlib':
            from .matplotlib import Fig1d as Fig1dMpl
            return Fig1dMpl
        elif self['2d'] == 'plotly':
            from .plotly import Fig1d as Fig1dPlotly
            return Fig1dPlotly
        raise ValueError(f'Unsupported backend {self["2d"]} for Fig1d.')

    @property
    def Fig2d(self):
        if self.backend == 'matplotlib':
            from .matplotlib import Fig2d as Fig2dMpl
            return Fig2dMpl
        raise ValueError(f'Unsupported backend {self["2d"]} for Fig2d.')
