# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Scipp contributors (https://github.com/scipp)

import scipp as sc

from .canvas import Canvas
from .fast_image import FastImage
from .mesh_image import MeshImage


def Image(
    canvas: Canvas,
    data: sc.DataArray,
    **kwargs,
):
    """
    Factory function to create an image artist.
    If all the coordinates of the data are 1D and linearly spaced,
    a `FastImage` is created.
    Otherwise, a `MeshImage` is created.

    Parameters
    ----------
    canvas:
        The canvas that will display the image.
    data:
        The data to create the image from.
    """
    if (canvas.ax.name != 'polar') and all(
        (data.coords[dim].ndim < 2)
        and ((data.coords[dim].dtype == str) or (sc.islinspace(data.coords[dim])))
        for dim in data.dims
    ):
        return FastImage(canvas=canvas, data=data, **kwargs)
    else:
        return MeshImage(canvas=canvas, data=data, **kwargs)
