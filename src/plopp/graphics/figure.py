# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from .. import backends


def figure1d(*args, style='line', **kwargs):

    if style == 'line':
        from .figline import FigLine

        return backends.figure1d(*args, FigConstructor=FigLine, **kwargs)

    raise ValueError(f'Unsupported style={style} for figure1d.')


def figure2d(*args, style='image', **kwargs):

    if style == 'image':
        from .figimage import FigImage

        return backends.figure2d(*args, FigConstructor=FigImage, **kwargs)

    raise ValueError(f'Unsupported style={style} for figure2d.')


def figure3d(*args, style='scatter', **kwargs):

    if style == 'scatter':
        from .figscatter3d import FigScatter3d

        return backends.figure3d(*args, FigConstructor=FigScatter3d, **kwargs)

    raise ValueError(f'Unsupported style={style} for figure3d.')
