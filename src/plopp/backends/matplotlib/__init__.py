# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)


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
        """
        Returns ``True`` if the backend currently in use allows for interactive figures.
        """
        from .utils import is_interactive_backend
        return is_interactive_backend()

    def canvas2d(self, *args, **kwargs):
        """
        See :class:`canvas.Canvas` for details.
        """
        from .canvas import Canvas as CanvasMpl
        return CanvasMpl(*args, **kwargs)

    def line(self, *args, **kwargs):
        """
        See :class:`line.Line` for details.
        """
        from .line import Line as LineMpl
        return LineMpl(*args, **kwargs)

    def image(self, *args, **kwargs):
        """
        See :class:`image.Image` for details.
        """
        from .image import Image as ImageMpl
        return ImageMpl(*args, **kwargs)

    def figure1d(self, *args, **kwargs):
        """
        See :class:`static.StaticFig` and :class:`interactive.InteractiveFig` for
        details.
        """
        return _make_figure(*args, **kwargs)

    def figure2d(self, *args, **kwargs):
        """
        See :class:`static.StaticFig` and :class:`interactive.InteractiveFig` for
        details.
        """
        return _make_figure(*args, **kwargs)
