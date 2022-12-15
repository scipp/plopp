# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

# flake8: noqa E402, F401

from . import plotly
from . import matplotlib


class Backend:

    def __init__(self, kind='matplotlib'):
        if kind == 'matplotlib':
            self.canvas = matplotlib.Canvas
            self.line = matplotlib.Line
        elif kind == 'plotly':
            self.canvas = plotly.Canvas
            self.line = plotly.Line

    def switch(self, kind):
        if kind == 'matplotlib':
            self.canvas = matplotlib.Canvas
            self.line = matplotlib.Line
        elif kind == 'plotly':
            self.canvas = plotly.Canvas
            self.line = plotly.Line
