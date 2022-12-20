# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from matplotlib import get_backend


def is_interactive_backend():
    """
    Return `True` if the current backend used by Matplotlib is the widget backend.
    """
    return 'ipympl' in get_backend()


# def figure1d(*args, **kwargs):
#     """
#     Make a 1d figure that is either static or interactive depending on the backend in
#     use.
#     """
#     if is_interactive_backend():
#         from .interactive import InteractiveFig1d
#         return InteractiveFig1d(*args, **kwargs)
#     else:
#         from .static import StaticFig1d
#         return StaticFig1d(*args, **kwargs)

# def figure2d(*args, **kwargs):
#     """
#     Make a 2d figure that is either static or interactive depending on the backend in
#     use.
#     """
#     if is_interactive_backend():
#         from .interactive import InteractiveFig2d
#         return InteractiveFig2d(*args, **kwargs)
#     else:
#         from .static import StaticFig2d
#         return StaticFig2d(*args, **kwargs)


class Fig1d:

    def __new__(cls, *args, FigConstructor, **kwargs):
        if is_interactive_backend():
            from .interactive import InteractiveFig1d
            return InteractiveFig1d(*args, FigConstructor=FigConstructor, **kwargs)
        else:
            from .static import StaticFig
            return StaticFig(*args, FigConstructor=FigConstructor, **kwargs)


class Fig2d:

    def __new__(cls, *args, FigConstructor, **kwargs):
        if is_interactive_backend():
            from .interactive import InteractiveFig2d
            return InteractiveFig2d(*args, FigConstructor=FigConstructor, **kwargs)
        else:
            from .static import StaticFig
            return StaticFig(*args, FigConstructor=FigConstructor, **kwargs)


# def figure3d(*args, **kwargs):
#     """
#     Make a 3d figure.
#     """
#     from .interactive import InteractiveFig3d
#     return InteractiveFig3d(*args, **kwargs)
