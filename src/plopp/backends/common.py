# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from __future__ import annotations

import numpy as np
import scipp as sc

from ..core.utils import merge_masks


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
