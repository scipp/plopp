# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import uuid
from typing import Literal

import numpy as np
import scipp as sc

from ..core.utils import merge_masks
from ..graphics.bbox import BoundingBox, axis_bounds


def check_ndim(data: sc.DataArray, ndim: int, origin: str) -> None:
    """
    Check the dimensionality of the data array.
    If the data array does not have the expected dimensionality, a ValueError is raised.

    Parameters
    ----------
    data:
        The data array to check.
    ndim:
        The expected dimensionality of the data array.
    origin:
        The name of the function that called this function.
    """
    if data.ndim != ndim:
        raise sc.DimensionError(
            f'{origin} only accepts data with {ndim} dimension(s), '
            f'found {data.ndim} dimension(s).'
        )


def make_line_data(data: sc.DataArray, dim: str) -> dict:
    """
    Prepare data for plotting a line.
    This includes extracting the x and y values, and optionally the error bars and masks
    from the data array.
    This also handles the case where the data array is a histogram, in which case the
    first bin edge is repeated.

    Parameters
    ----------
    data:
        The data array to extract values from.
    dim:
        The dimension along which to extract values.
    """
    x = data.coords[dim]
    y = data.data
    hist = len(x) != len(y)
    error = None
    xvalues = np.asarray(x.values)
    yvalues = np.asarray(y.values)
    values = {'x': xvalues, 'y': yvalues}
    mask = {'x': xvalues, 'y': np.full(y.shape, np.nan), 'visible': False}
    if data.variances is not None:
        error = {
            'x': np.asarray(sc.midpoints(x).values) if hist else xvalues,
            'y': yvalues,
            'e': np.asarray(sc.stddevs(y).values),
        }
    if len(data.masks):
        one_mask = np.asarray(merge_masks(data.masks).values)
        mask = {
            'x': xvalues,
            'y': np.where(one_mask, yvalues, np.nan),
            'visible': True,
        }
    if hist:
        for array in (values, mask):
            array['y'] = np.concatenate([array['y'][0:1], array['y']])
    return {'values': values, 'stddevs': error, 'mask': mask, 'hist': hist}


def make_line_bbox(
    data: sc.DataArray,
    dim: str,
    errorbars: bool,
    xscale: Literal['linear', 'log'],
    yscale: Literal['linear', 'log'],
) -> BoundingBox:
    """
    Calculate the bounding box of a line artist.
    This includes the x and y bounds of the line and optionally the error bars.

    Parameters
    ----------
    data:
        The data array to extract values from.
    dim:
        The dimension along which to extract values.
    errorbars:
        Whether to include error bars in the bounding box.
    xscale:
        The scale of the x-axis.
    yscale:
        The scale of the y-axis.
    """
    line_x = data.coords[dim]
    if errorbars:
        stddevs = sc.stddevs(data.data)
        line_y = sc.DataArray(
            data=sc.concat(
                [data.data - stddevs, data.data + stddevs], dim=uuid.uuid4().hex
            ),
            masks=data.masks,
        )
    else:
        line_y = data

    return BoundingBox(
        **{**axis_bounds(('xmin', 'xmax'), line_x, xscale, pad=True)},
        **{**axis_bounds(('ymin', 'ymax'), line_y, yscale, pad=True)},
    )
