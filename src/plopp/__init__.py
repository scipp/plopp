# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026 Scipp contributors (https://github.com/scipp)
# ruff: noqa: RUF100, E402, F401, I

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
            'DimensionSlicer',
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

# Workaround for thread-safety issues in matplotlib's mathtext parser.
# The _mathtext.Parser singleton has mutable state (_state_stack, etc.) that is
# not protected against concurrent access from multiple threads. When ipympl is
# used with ipykernel >= 7 (which introduces additional threads for message
# routing), concurrent calls to the parser can corrupt this state, leading to
# ParseException errors like 'Expected end of text, found "$"'.
# See https://github.com/matplotlib/ipympl/issues/610
try:
    import functools
    from threading import Lock

    from matplotlib._mathtext import Parser as _MathTextInternalParser

    _mathtext_parse_lock = Lock()
    _original_mathtext_parse = _MathTextInternalParser.parse

    @functools.wraps(_original_mathtext_parse)
    def _thread_safe_mathtext_parse(self, *args, **kwargs):
        with _mathtext_parse_lock:
            return _original_mathtext_parse(self, *args, **kwargs)

    _MathTextInternalParser.parse = _thread_safe_mathtext_parse
except Exception:
    pass

del importlib
