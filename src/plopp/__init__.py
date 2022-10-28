# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

# flake8: noqa E402, F401

import importlib.metadata
try:
    __version__ = importlib.metadata.version(__package__ or __name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"

from .core import Node, View, node, input_node, widget_node, show_graph
from .functions import figure1d, figure2d, plot, slicer, inspector, scatter3d, superplot

from . import data


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


def unpatch_scipp():
    """
    Running this reverts the patching operation in :func:`patch_scipp`.
    """
    import scipp as sc
    from scipp.plotting import plot as pl
    setattr(sc.Variable, 'plot', pl)
    setattr(sc.DataArray, 'plot', pl)
    setattr(sc.Dataset, 'plot', pl)
    setattr(sc, 'plot', pl)
