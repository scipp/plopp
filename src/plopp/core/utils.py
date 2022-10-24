# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

import scipp as sc
import uuid
from functools import reduce


def coord_as_bin_edges(da, key, dim=None):
    """
    If coordinate `key` in DataArray da is already bin edges, return it unchanged.
    If it is midpoints, return as bin edges.
    """
    if dim is None:
        dim = key
    x = da.meta[key]
    if x.dtype == str:
        x = sc.arange(dim, float(x.shape[0]), unit=x.unit)
    if da.meta.is_edges(key, dim=dim):
        return x
    if x.sizes[dim] < 2:
        half = sc.scalar(0.5, unit=x.unit)
        return sc.concat([x[dim, 0:1] - half, x[dim, 0:1] + half], dim)
    else:
        center = sc.midpoints(x, dim=dim)
        # Note: use range of 0:1 to keep dimension dim in the slice to avoid
        # switching round dimension order in concatenate step.
        left = center[dim, 0:1] - (x[dim, 1] - x[dim, 0])
        right = center[dim, -1] + (x[dim, -1] - x[dim, -2])
        return sc.concat([left, center, right], dim)


def repeat(x, dim, n):
    """
    Equivalent of Numpy's `repeat` function: repeat the values of a variable `n` times
    along dimension `dim`.
    """
    index = x.dims.index(dim) + 1
    dummy_dim = uuid.uuid4().hex
    new_dims = list(x.dims)
    new_dims.insert(index, dummy_dim)
    new_shape = list(x.shape)
    new_shape.insert(index, n)
    return x.broadcast(dims=new_dims, shape=new_shape).flatten(dims=[dim, dummy_dim],
                                                               to=dim)


def number_to_variable(x):
    """
    Convert the input int or float to a variable.
    """
    return sc.scalar(x, unit=None) if isinstance(x, (int, float)) else x


def name_with_unit(var=None, name=None, log=False):
    """
    Make a column title or axis label with "Name [unit]".
    """
    text = ""
    if name is not None:
        text = name
    elif var is not None:
        text = str(var.dims[-1])

    if log:
        text = "log\u2081\u2080(" + text + ")"
    if var is not None:
        unit = var.unit if var.bins is None else var.bins.constituents["data"].unit
        if unit is not None:
            text += f" [{unit}]"
    return text


def value_to_string(val, precision=3):
    """
    Convert a number to a human readable string.
    """
    if (not isinstance(val, float)) or (val == 0):
        text = str(val)
    elif (abs(val) >= 10.0**(precision+1)) or \
         (abs(val) <= 10.0**(-precision-1)):
        text = "{val:.{prec}e}".format(val=val, prec=precision)
    else:
        text = "{}".format(val)
        if len(text) > precision + 2 + (text[0] == '-'):
            text = "{val:.{prec}f}".format(val=val, prec=precision)
    return text


def merge_masks(masks):
    """
    Combine all masks into a single one using the OR operation.
    """
    return reduce(lambda a, b: a | b, masks.values())


def coord_element_to_string(coord):
    """
    Convert a slice of a coordinate containing a single value (or two values in the
    case of a bin-edge coordinate) to a string.
    """
    out = value_to_string(coord.values)
    if coord.unit is not None:
        out += f" [{coord.unit}]"
    return out
