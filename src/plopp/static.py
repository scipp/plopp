# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .figure import Figure
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
        Convert the Matplotlib figure to a widget. If the ipympl (widget)
        backend is in use, return the custom toolbar and the figure canvas.
        If not, convert the plot to a png image and place inside an ipywidgets
        Image container.
        """
        import ipywidgets as ipw
        width, height = self._fig.get_size_inches()
        dpi = self._fig.get_dpi()
        canvas = ipw.Image(value=fig_to_bytes(self._fig),
                           width=width * dpi,
                           height=height * dpi)
        return ipw.VBox([
            self.top_bar.to_widget(),
            ipw.HBox([self.left_bar.to_widget(), canvas,
                      self.right_bar.to_widget()]),
            self.bottom_bar.to_widget()
        ])
