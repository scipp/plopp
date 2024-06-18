# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)
# import sys
# from functools import partial

# from .. import dispatcher
# from ..core.typing import FigureLike
from .basefig import BaseFig
from .camera import Camera
from .colormapper import ColorMapper
from .figure import figure1d, figure2d, figure3d
from .figures import linefigure, imagefigure, scatterfigure
from .graphicalview import GraphicalView

# from .imageview import ImageView  # , imagefigure
# from .lineview import LineView  # , linefigure
from .scatter3dview import Scatter3dView, scatter3dfigure

# from .scatterview import ScatterView  # , scatterfigure
from .tiled import tiled


# for name in ['line']:

#     def figure_func(*nodes, **kwargs) -> FigureLike:
#         params = dispatcher.module(name).PARAMETERS
#         view_maker = partial(GraphicalView, **params)
#         return dispatcher['figure'](view_maker, *nodes, **kwargs)

#     setattr(sys.modules[__name__], f'{name}figure', figure_func)


__all__ = [
    'BaseFig',
    'Camera',
    'ColorMapper',
    'GraphicalView',
    # 'ImageView',
    'Scatter3dView',
    # 'ScatterView',
    'figure1d',
    'figure2d',
    'figure3d',
    'imagefigure',
    # 'LineView',
    'linefigure',
    'scatter3dfigure',
    'scatterfigure',
    'tiled',
]
