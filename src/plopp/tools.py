# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from scipp import scalar, concat, midpoints


def to_bin_edges(x, dim):
    """
    Convert array centers to edges
    """
    idim = x.dims.index(dim)
    if x.shape[idim] < 2:
        half = scalar(0.5, unit=x.unit)
        return concat([x[dim, 0:1] - half, x[dim, 0:1] + half], dim)
    else:
        center = midpoints(x, dim=dim)
        # Note: use range of 0:1 to keep dimension dim in the slice to avoid
        # switching round dimension order in concatenate step.
        left = center[dim, 0:1] - (x[dim, 1] - x[dim, 0])
        right = center[dim, -1] + (x[dim, -1] - x[dim, -2])
        return concat([left, center, right], dim)


def number_to_variable(x):
    """
    Convert the input int or float to a variable.
    """
    return scalar(x, unit=None) if isinstance(x, (int, float)) else x


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
