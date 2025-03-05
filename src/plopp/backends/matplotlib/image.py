# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

import scipp as sc

from .fast_image import FastImage
from .mesh_image import MeshImage


def Image(
    *,
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
    data:
        The data to create the image from.
    """
    if all(
        (sc.islinspace(data.coords[dim]) and (data.coords[dim].ndim < 2))
        for dim in data.dims
    ):
        return FastImage(data=data, **kwargs)
    else:
        return MeshImage(data=data, **kwargs)
