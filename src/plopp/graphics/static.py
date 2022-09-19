# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .fig import Figure
from .io import fig_to_bytes


class StaticFig(Figure):

    def _repr_mimebundle_(self, include=None, exclude=None):
        """
        Mimebundle display representation for jupyter notebooks.
        """
        return {
            'text/plain': 'Figure',
            'image/svg+xml': fig_to_bytes(self._fig, form='svg').decode()
        }

    def to_widget(self):
        """
        Convert the Matplotlib figure to an image widget.
        """
        return self._to_image()
