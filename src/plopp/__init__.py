# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

# flake8: noqa E402

import importlib.metadata

try:
    __version__ = importlib.metadata.version(__package__ or __name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"

from .backends.manager import BackendManager

backends = BackendManager()

from . import data
from .core import Node, View, node, show_graph, widget_node
from .graphics import (
    Camera,
    figure1d,
    figure2d,
    figure3d,
    imagefigure,
    linefigure,
    scatterfigure,
    scatter3dfigure,
    tiled,
)
from .plotting import inspector, plot, scatter, scatter3d, slicer, superplot, xyplot

del importlib


def show():
    """
    A function to display all the currently opened figures (note that this only applies
    to the figures created via the Matplotlib backend).
    See https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.show.html for more
    details.
    """
    import matplotlib.pyplot as plt

    plt.show()


__all__ = [
    'Camera',
    'Node',
    'View',
    'backends',
    'data',
    'figure1d',
    'figure2d',
    'figure3d',
    'imagefigure',
    'inspector',
    'linefigure',
    'node',
    'plot',
    'scatter',
    'scatterfigure',
    'scatter3d',
    'scatter3dfigure',
    'show',
    'show_graph',
    'slicer',
    'superplot',
    'tiled',
    'widget_node',
    'xyplot',
]
