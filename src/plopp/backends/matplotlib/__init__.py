# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)


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
        from .figure import figure1d as fig1d_mpl
        return fig1d_mpl(*args, **kwargs)

    def figure2d(self, *args, **kwargs):
        from .figure import figure2d as fig2d_mpl
        return fig2d_mpl(*args, **kwargs)
