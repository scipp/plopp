# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

# from dataclasses import dataclass
import uuid
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image as PilImage
import scipp as sc

from ...core.utils import merge_masks
from ...core.limits import find_limits, fix_empty_range
from ..matplotlib.image import Image as MplImage
from ..matplotlib.canvas import Canvas as MplCanvas
from ..matplotlib.utils import silent_mpl_figure

from .canvas import Canvas

import plotly.graph_objects as go


# @dataclass
# class DummyCanvas:
#     ax: plt.Axes

#     def draw(self):
#         pass

#     def register_format_coord(self, func):
#         pass


class Image:
    """
    Artist to represent two-dimensional data.
    """

    def __init__(self, canvas: Canvas, data: sc.DataArray, **kwargs):
        self._fig = canvas.fig
        self._data = data
        self._id = uuid.uuid4().hex

        with silent_mpl_figure():
            fig = plt.figure(dpi=300)
            ax = fig.add_axes([0, 0, 1, 1])
        # mpl_canvas = DummyCanvas(ax=ax)
        ax.set_axis_off()
        self._mpl_canvas = MplCanvas(ax=ax, cbar=False)
        self._mpl_image = MplImage(canvas=self._mpl_canvas, data=data, **kwargs)
        # s, (width, height) = fig.canvas.print_to_buffer()
        # X = np.flipud(np.frombuffer(s, np.uint8).reshape((height, width, 4)))

        # img = PilImage.fromarray(X)
        # img.save('pillimg.png')

        # Now the plotly code
        # import plotly.graph_objects as go

        # # Create figure
        # fig = go.FigureWidget()

        # # Constants
        # img_width = 900
        # img_height = 600

        coords = self._mpl_image._mesh.get_coordinates()
        left, right = fix_empty_range(
            find_limits(
                sc.array(dims=['x', 'y'], values=coords[..., 0]),
                scale=canvas.xscale,
            )
        )
        bottom, top = fix_empty_range(
            find_limits(
                sc.array(dims=['x', 'y'], values=coords[..., 1]),
                scale=canvas.yscale,
            )
        )
        self.xmin = left.value
        self.xmax = right.value
        self.ymin = bottom.value
        self.ymax = top.value

        # xcoord = self._mpl_image._data_with_bin_edges.coords[self._data.dims[1]]
        # ycoord = self._mpl_image._data_with_bin_edges.coords[self._data.dims[0]]
        # self.xmin = xcoord.values[0]
        # self.xmax = xcoord.values[-1]
        # self.ymin = ycoord.values[0]
        # self.ymax = ycoord.values[-1]

        # Add invisible scatter trace.
        # This trace is added to help the autoresize logic work.
        # We also add a color to the scatter points so we can have a colorbar next to our image
        self._fig.add_trace(
            go.Scatter(
                x=[self.xmin, self.xmax],
                y=[self.ymin, self.ymax],
                mode="markers",
                marker={
                    # "color":[np.amin(a), np.amax(a)],
                    #     "colorscale":'Viridis',
                    #     "showscale":True,
                    #     "colorbar":{"title":"Counts",
                    #                 "titleside": "right"},
                    "opacity": 0
                },
            )
        )

        # Add image
        # logx = canvas.xscale == 'log'
        # logy = canvas.yscale == 'log'
        self._xscale = canvas.xscale
        self._yscale = canvas.yscale

        # self._fig.update_layout(
        #     images=[
        #         go.layout.Image(
        #             x=xmin,
        #             sizex=xmax - xmin,
        #             y=ymax,
        #             sizey=ymax - ymin,
        #             xref="x",
        #             yref="y",
        #             opacity=1.0,
        #             layer="below",
        #             sizing="stretch",
        #             source=img,
        #         )
        #     ]
        # )

        # Configure other layout
        self._fig.update_layout(
            xaxis=dict(showgrid=False, zeroline=False, range=[self.xmin, self.xmax]),
            yaxis=dict(showgrid=False, zeroline=False, range=[self.ymin, self.ymax]),
            # width=img_width,
            # height=img_height,
        )

        # fig.show()

    def set_colors(self, rgba: np.ndarray):
        """
        Set the mesh's rgba colors:

        Parameters
        ----------
        rgba:
            The array of rgba colors.
        """
        self._mpl_image.set_colors(rgba)
        self.redraw()

    def redraw(self, xscale=None, yscale=None):
        if xscale is None:
            xscale = self._xscale
        else:
            self._mpl_canvas.xscale = xscale
        if yscale is None:
            yscale = self._yscale
        else:
            self._mpl_canvas.yscale = yscale
        self._xscale = xscale
        self._yscale = yscale

        s, (width, height) = self._mpl_image._ax.get_figure().canvas.print_to_buffer()
        X = np.frombuffer(s, np.uint8).reshape((height, width, 4))
        img = PilImage.fromarray(X)

        # TODO: need to fix log when xmin is non-positive
        x = np.log10(self.xmin) if self._xscale == 'log' else self.xmin
        sizex = (
            (np.log10(self.xmax) - np.log10(self.xmin))
            if self._xscale == 'log'
            else (self.xmax - self.xmin)
        )
        y = np.log10(self.ymax) if self._yscale == 'log' else self.ymax
        sizey = (
            (np.log10(self.ymax) - np.log10(self.ymin))
            if self._yscale == 'log'
            else (self.ymax - self.ymin)
        )

        self._fig.update_layout(
            images=[
                go.layout.Image(
                    x=x,
                    sizex=sizex,
                    y=y,
                    sizey=sizey,
                    xref="x",
                    yref="y",
                    opacity=1.0,
                    layer="below",
                    sizing="stretch",
                    source=img,
                )
            ]
        )
        self._fig.layout.images[0]._plopp_parent = self

    def update(self, new_values: sc.DataArray):
        """
        Update the x and y positions of the data points from new data.

        Parameters
        ----------
        new_values:
            New data to update the line values, masks, errorbars from.
        """

        self._data = new_values
        self._mpl_image.update(new_values)
        # s, (width, height) = self._mpl_image._ax.get_figure().canvas.print_to_buffer()
        # X = np.flipud(np.frombuffer(s, np.uint8).reshape((height, width, 4)))
        # img = PilImage.fromarray(X)
        # # img.save('pillimg.png')
        # self._fig.update_layout(
        #     images=[
        #         go.layout.Image(
        #             x=self.xmin,
        #             sizex=self.xmax - self.xmin,
        #             y=self.ymax,
        #             sizey=self.ymax - self.ymin,
        #             xref="x",
        #             yref="y",
        #             opacity=1.0,
        #             layer="below",
        #             sizing="stretch",
        #             source=img,
        #         )
        #     ]
        # )

    @property
    def data(self):
        return self._mpl_image.data
