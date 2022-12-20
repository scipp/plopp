# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)


class Config:

    def __init__(self, backend='matplotlib'):
        self.backend = backend

    @property
    def Canvas(self):
        if self.backend == 'matplotlib':
            from .backends.matplotlib import Canvas as CanvasMpl
            return CanvasMpl
        # elif self.backend == 'plotly':
        #     from .backends.plotly import Canvas as CanvasPlotly
        #     return CanvasPlotly

    @property
    def Line(self):
        if self.backend == 'matplotlib':
            from .backends.matplotlib import Line as LineMpl
            return LineMpl
        # elif self.backend == 'plotly':
        #     from .backends.plotly import Line as LinePlotly
        #     return LinePlotly

    @property
    def Mesh(self):
        if self.backend == 'matplotlib':
            from .backends.matplotlib import Mesh as MeshMpl
            return MeshMpl
        # elif self.backend == 'plotly':
        #     from .backends.plotly import Mesh as MeshPlotly
        #     return MeshPlotly

    # def Fig1d(self, *args, **kwargs):
    #     if self.backend == 'matplotlib':
    #         from .backends.matplotlib import figure1d as fig1d_mpl
    #         return fig1d_mpl(*args, **kwargs)
    #     # elif self.backend == 'plotly':
    #     #     from .backends.plotly import figure1d as fig1d_plotly
    #     #     return fig1d_plotly(*args, **kwargs)

    def Fig1d(self, *args, FigConstructor, **kwargs):
        if self.backend == 'matplotlib':
            from .backends.matplotlib import Fig1d as Fig1d_mpl
            return Fig1d_mpl(*args, FigConstructor=FigConstructor, **kwargs)

    def Fig2d(self, *args, FigConstructor, **kwargs):
        if self.backend == 'matplotlib':
            from .backends.matplotlib import Fig2d as Fig2d_mpl
            return Fig2d_mpl(*args, FigConstructor=FigConstructor, **kwargs)
        # elif self.backend == 'plotly':
        #     from .backends.plotly import figure2d as fig2d_plotly
        #     return fig2d_plotly(*args, **kwargs)


# def line(backend):

#     if backend == 'matplotlib':
#         return matplotlib.Line
#     elif backend == 'plotly':
#         return plotly.Line

# def figure1d(backend):

#     if backend == 'matplotlib':
#         return matplotlib.Canvas
#     elif backend == 'plotly':
#         return plotly.Canvas
