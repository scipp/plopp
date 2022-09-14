# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

# flake8: noqa E402, F401

import importlib.metadata
try:
    __version__ = importlib.metadata.version(__package__ or __name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"

import matplotlib.pyplot as plt

plt.ioff()

from .graph import show_graph
from .plot import Plot
from .model import Node, node, input_node
from .wrappers import plot, figure

from . import data
from . import widgets


def patch_scipp():
    """
    Running this replaces the `plot` function from Scipp with the plopp `plot` wrapper.
    This patches the Variable, DataArray, Dataset classes, as well as the main `plot`
    function in the Scipp module.
    """
    import scipp as sc
    setattr(sc.Variable, 'plot', plot)
    setattr(sc.DataArray, 'plot', plot)
    setattr(sc.Dataset, 'plot', plot)
    setattr(sc, 'plot', plot)
