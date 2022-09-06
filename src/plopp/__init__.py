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
from .figure import Figure
from . import widgets
from .wrappers import plot
