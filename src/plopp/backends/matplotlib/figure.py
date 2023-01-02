# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .utils import is_interactive_backend


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
