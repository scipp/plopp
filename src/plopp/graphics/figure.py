# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .. import backends

# from .common import is_interactive_backend

# def figure1d(*args, **kwargs):
#     """
#     Make a 1d figure that is either static or interactive depending on the backend in
#     use.
#     """
#     if is_interactive_backend():
#         from ..graphics.interactive import InteractiveFig1d
#         return InteractiveFig1d(*args, **kwargs)
#     else:
#         from ..graphics import StaticFig1d
#         return StaticFig1d(*args, **kwargs)

# def figure2d(*args, **kwargs):
#     """
#     Make a 2d figure that is either static or interactive depending on the backend in
#     use.
#     """
#     if is_interactive_backend():
#         from ..graphics.interactive import InteractiveFig2d
#         return InteractiveFig2d(*args, **kwargs)
#     else:
#         from ..graphics import StaticFig2d
#         return StaticFig2d(*args, **kwargs)

# def figure3d(*args, **kwargs):
#     """
#     Make a 3d figure.
#     """
#     from ..graphics.interactive import InteractiveFig3d
#     return InteractiveFig3d(*args, **kwargs)


def figure1d(*args, mode='line', **kwargs):

    if mode == 'line':
        # from ..configfig2d import Fig2d
        from .figline import FigLine

        return backends.Fig1d(*args, FigConstructor=FigLine, **kwargs)

    raise ValueError(f'Unsupported mode={mode} for figure1d.')


def figure2d(*args, mode='image', **kwargs):

    if mode == 'image':
        # from ..configfig2d import Fig2d
        from .figimage import FigImage

        return backends.Fig2d(*args, FigConstructor=FigImage, **kwargs)

    raise ValueError(f'Unsupported mode={mode} for figure2d.')


def figure3d(*args, mode='scatter', **kwargs):

    if mode == 'scatter':
        # from .fig3d import Fig3d
        from .figscatter3d import FigScatter3d

        return backends.Fig3d(*args, FigConstructor=FigScatter3d, **kwargs)

    raise ValueError(f'Unsupported mode={mode} for figure3d.')
