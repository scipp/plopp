# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import uuid
from functools import reduce
from typing import Dict, Optional, Union

import scipp as sc


def coord_as_bin_edges(da: sc.DataArray, key: str, dim: str = None) -> sc.Variable:
    """
    If coordinate ``key`` in DataArray ``da`` is already bin edges, return it unchanged.
    If it is midpoints, return as bin edges.

    Parameters
    ----------
    da:
        The input data array.
    key:
        The name of coordinate to potentially convert to bin edges.
    dim:
        The dimension to use for computing the bin edges (this can be different from
        the coordinate name, in the case of non-dimension coordinates).
    """
    if dim is None:
        dim = key
    x = da.meta[key]
    if x.dtype == str:
        x = sc.arange(dim, float(x.shape[0]), unit=x.unit)
    if da.meta.is_edges(key, dim=dim):
        return x
    if x.dtype in ('int32', 'int64'):
        x = x.to(dtype='float64')
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


def repeat(x: sc.Variable, dim: str, n: int) -> sc.Variable:
    """
    Equivalent of Numpy's `repeat` function: repeat the values of a variable `n` times
    along dimension `dim`.

    Parameters
    ----------
    x:
        The input variable.
    dim:
        The dimension along which to repeat.
    n:
        The number of times to repeat.
    """
    index = x.dims.index(dim) + 1
    dummy_dim = uuid.uuid4().hex
    new_dims = list(x.dims)
    new_dims.insert(index, dummy_dim)
    new_shape = list(x.shape)
    new_shape.insert(index, n)
    return x.broadcast(dims=new_dims, shape=new_shape).flatten(dims=[dim, dummy_dim],
                                                               to=dim)


def number_to_variable(x: Union[int, float, sc.Variable], unit: str) -> sc.Variable:
    """
    Convert the input int or float to a variable.

    Parameters
    ----------
    x:
        The input int or float.
    """
    return sc.scalar(x, unit=unit) if isinstance(x, (int, float)) else x.to(unit=unit)


def maybe_variable_to_number(x: Union[int, float, sc.Variable],
                             unit=None) -> Union[int, float]:
    """
    If the input is a variable, return its value.
    If a unit is requested, perform the conversion to that unit first.
    If the input is a number, return it unchanged.

    Parameters
    ----------
    x:
        The input number or variable.
    unit:
        Convert the input to that unit if not ``None``.
    """
    if hasattr(x, 'unit'):
        if unit is not None:
            x = x.to(unit=unit)
        x = x.values
    return x


def name_with_unit(var: sc.Variable, name: str = None) -> str:
    """
    Make a string from a variable dimension and its unit.
    The variable dimension can be overridden by specifying the ``name`` directly.

    Parameters
    ----------
    var:
        The input variable.
    name:
        The name to use to override the variable's dimension name.
    """
    text = ""
    if name is not None:
        text = name
    else:
        text = str(var.dims[-1])
    if var.unit is not None:
        text += f" [{var.unit}]"
    return text


def value_to_string(val: Union[int, float], precision: int = 3) -> str:
    """
    Convert a number to a human readable string.

    Parameters
    ----------
    val:
        The input number.
    precision:
        The number of decimal places to use for the string output.
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


def merge_masks(masks: Dict[str, sc.Variable]) -> sc.Variable:
    """
    Combine all masks into a single one using the OR operation.

    Parameters
    ----------
    masks:
        The dict holding the masks to be combined.
    """
    return reduce(lambda a, b: a | b, masks.values())


def coord_element_to_string(x: sc.Variable) -> str:
    """
    Convert a slice of a coordinate containing a single value (or two values in the
    case of a bin-edge coordinate) to a string.

    Parameters
    ----------
    x:
        The input variable (of length 1 or 2).
    """
    out = value_to_string(x.values)
    if x.unit is not None:
        out += f" [{x.unit}]"
    return out


def make_compatible(x: sc.Variable,
                    *,
                    unit: Union[str, None],
                    dim: Optional[str] = None):
    """
    Raise exception if the dimensions of the supplied variable do not contain the
    requested dimension.
    Then, if the variable unit differs from the requested unit, attempt a conversion.

    Parameters
    ----------
    x:
        The input variable.
    unit:
        Attempt unit conversion to this unit if the input variable has a different unit.
    dim:
        If supplied, check that the dim is found in the input variable's dimensions.
    """
    if (dim is not None) and (dim not in x.dims):
        raise sc.DimensionError(
            f'The supplied variable has dimension {x.dims} which is '
            f'incompatible with the requested dimension {dim}.')
    if x.unit != unit:
        if unit is not None:
            return x.to(unit=unit, dtype=float)
        else:
            raise sc.UnitError(f'The supplied variable has unit {x.unit} which is '
                               'incompatible with the requested unit None/<no unit>.')
    return x
