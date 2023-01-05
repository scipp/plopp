# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)


def _make_figure(*args, **kwargs):
    from .utils import is_interactive_backend
    if is_interactive_backend():
        from .interactive import InteractiveFig
        return InteractiveFig(*args, **kwargs)
    else:
        from .static import StaticFig
        return StaticFig(*args, **kwargs)


class MatplotlibBackend:

    def is_interactive(self):
        from .utils import is_interactive_backend
        return is_interactive_backend()

    def canvas2d(self, *args, **kwargs):
        from .canvas import Canvas as CanvasMpl
        return CanvasMpl(*args, **kwargs)

    def line(self, *args, **kwargs):
        from .line import Line as LineMpl
        return LineMpl(*args, **kwargs)

    def image(self, *args, **kwargs):
        from .image import Image as ImageMpl
        return ImageMpl(*args, **kwargs)

    def figure1d(self, *args, **kwargs):
        return _make_figure(*args, **kwargs)

    def figure2d(self, *args, **kwargs):
        return _make_figure(*args, **kwargs)
