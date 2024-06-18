# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from .basefig import BaseFig
from .camera import Camera
from .colormapper import ColorMapper
from .figure import figure1d, figure2d, figure3d

# from .imageview import ImageView, imagefigure
# from .lineview import LineView, linefigure
from .imageview import imagefigure
from .lineview import linefigure
from .mesh3dview import Mesh3dView, mesh3dfigure
from .scatter3dview import Scatter3dView, scatter3dfigure

# from .scatterview import ScatterView, scatterfigure
from .scatterview import scatterfigure
from .tiled import tiled

__all__ = [
    'BaseFig',
    'Camera',
    'ColorMapper',
    # 'ImageView',
    # 'LineView',
    'Mesh3dView',
    'Scatter3dView',
    # 'ScatterView',
    'figure1d',
    'figure2d',
    'figure3d',
    'imagefigure',
    'linefigure',
    'mesh3dfigure',
    'scatter3dfigure',
    'scatterfigure',
    'tiled',
]
