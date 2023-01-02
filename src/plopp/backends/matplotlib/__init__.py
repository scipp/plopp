# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)


class MatplotlibBackend:

    @property
    def is_interactive(self):
        from .utils import is_interactive_backend
        return is_interactive_backend()

    @property
    def Canvas2d(self):
        from .canvas import Canvas as CanvasMpl
        return CanvasMpl

    @property
    def Line(self):
        from .line import Line as LineMpl
        return LineMpl

    @property
    def Image(self):
        from .image import Image as ImageMpl
        return ImageMpl

    @property
    def Fig1d(self):
        from .figure import Fig1d as Fig1dMpl
        return Fig1dMpl

    @property
    def Fig2d(self):
        from .figure import Fig2d as Fig2dMpl
        return Fig2dMpl
