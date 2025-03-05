# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Scipp contributors (https://github.com/scipp)
# ruff: noqa: E402, F401, I

import importlib.metadata

try:
    __version__ = importlib.metadata.version(__package__ or __name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"


import lazy_loader as lazy

__getattr__, __dir__, __all__ = lazy.attach(
    __name__,
    submodules=['data'],
    submod_attrs={
        'core': ['Node', 'View', 'node', 'show_graph', 'widget_node'],
        'graphics': [
            'Camera',
            'imagefigure',
            'linefigure',
            'scatter3dfigure',
            'scatterfigure',
            'tiled',
        ],
        'plotting': [
            'inspector',
            'mesh3d',
            'plot',
            'scatter',
            'scatter3d',
            'slicer',
            'superplot',
            'xyplot',
        ],
        'widgets': ['Box', 'Checkboxes', 'SliceWidget', 'slice_dims'],
    },
)

from .backends import BackendManager

backends = BackendManager()

del importlib
