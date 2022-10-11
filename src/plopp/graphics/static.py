# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .fig import Figure
from .fig2d import Figure2d
from .io import fig_to_bytes


class Static:

    def _repr_mimebundle_(self, include=None, exclude=None):
        """
        Mimebundle display representation for jupyter notebooks.
        """
        return {
            'text/plain': 'Figure',
            'image/svg+xml': self.canvas.to_bytes(form='svg').decode()
        }

    def to_widget(self):
        """
        Convert the Matplotlib figure to an image widget.
        """
        return self.canvas.to_image()


# class StaticFig1d(Static, Figure1d):
#     pass


class StaticFig2d(Static, Figure2d):
    pass
