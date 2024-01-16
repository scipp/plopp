# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import warnings
from typing import Any, Callable, List, Optional, Union

import numpy as np
import scipp as sc

from .. import backends
from ..core import Node
from ..core.typing import Plottable, PlottableMulti


def require_interactive_backend(func: str):
    """
    Raise an error if the current backend in use is non-interactive.
    """
    if not backends.is_interactive():
        raise RuntimeError(
            f"The {func} can only be used with an interactive backend "
            "backend. Use `%matplotlib widget` at the start of your "
            "notebook."
        )


def is_pandas_series(obj: Any) -> bool:
    """
    Check if an object is a pandas series.
    """
    try:
        import pandas as pd
    except ImportError:
        return False
    return isinstance(obj, pd.Series)


def from_compatible_lib(obj: Any) -> Any:
    """
    Convert from a compatible library, if possible.
    """
    if 'pandas' in str(type(obj)):
        return sc.compat.from_pandas(obj)
    if 'xarray' in str(type(obj)):
        return sc.compat.from_xarray(obj)
    return obj


def _maybe_to_variable(obj: Union[Plottable, list]) -> Plottable:
    """
    Attempt to convert the input to a Variable.
    If the input is either a list or a numpy array, it will be converted.
    Otherwise, the input will be returned unchanged.
    """
    out = obj
    if isinstance(out, list):
        out = np.array(out)
    if isinstance(out, np.ndarray):
        dims = [f"axis-{i}" for i in range(len(out.shape))]
        out = sc.Variable(dims=dims, values=out)
    return out


def to_variable(obj) -> sc.Variable:
    """
    Convert an input to a Variable. If the object returned by the conversion is not a
    Variable, raise an error.

    Parameters
    ----------
    obj:
        The input object to be converted.
    """
    out = _maybe_to_variable(obj)
    if not isinstance(out, sc.Variable):
        raise TypeError(f"Cannot convert input of type {type(obj)} to a Variable.")
    return out


def to_data_array(
    obj: Union[Plottable, list],
) -> sc.DataArray:
    """
    Convert an input to a DataArray, potentially adding fake coordinates if they are
    missing.

    Parameters
    ----------
    obj:
        The input object to be converted.
    """
    out = _maybe_to_variable(obj)
    if isinstance(out, sc.Variable):
        out = sc.DataArray(data=out)
    out = from_compatible_lib(out)
    if not isinstance(out, sc.DataArray):
        raise TypeError(f"Cannot convert input of type {type(obj)} to a DataArray.")
    out = out.copy(deep=False)
    for dim, size in out.sizes.items():
        if dim not in out.coords:
            out.coords[dim] = sc.arange(dim, size, unit=None)
    return out


def _check_size(da: sc.DataArray):
    """
    Prevent slow figure rendering by raising an error if the data array exceeds a
    default size.
    """
    limits = {1: 1_000_000, 2: 2500 * 2500}
    if da.ndim not in limits:
        raise ValueError("plot can only handle 1d and 2d data.")
    if np.prod(da.shape) > limits[da.ndim]:
        raise ValueError(
            f"Plotting data of size {da.shape} may take very long or use "
            "an excessive amount of memory. This is therefore disabled by "
            "default. To bypass this check, use `ignore_size=True`."
        )


def check_not_binned(da: sc.DataArray):
    """
    Plopp cannot plot binned data.
    This function will raise an error if the input data is binned.

    Parameters
    ----------
    da:
        The data array to be plotted.
    """
    if da.bins is not None:
        params = ', '.join([f'{dim}=100' for dim in da.dims])
        raise ValueError(
            "Cannot plot binned data, it must be histogrammed first, "
            f"e.g., using ``da.hist()`` or da.hist({params})``."
            "See https://scipp.github.io/generated/functions/scipp.hist.html for "
            "more details."
        )


def check_allowed_dtypes(da: sc.DataArray):
    """
    Currently, Plopp cannot plot data that contains vector and matrix dtypes.
    This function will raise an error if the input data type is not supported.

    Parameters
    ----------
    da:
        The data array to be plotted.
    """
    if da.shape != da.values.shape:
        raise TypeError(
            f'The input has dtype {da.dtype} which is not supported by Plopp.'
        )


def _all_dims_sorted(var, order='ascending'):
    return all([sc.allsorted(var, dim, order=order) for dim in var.dims])


def preprocess(
    obj: Union[Plottable, list],
    name: Optional[str] = None,
    ignore_size: bool = False,
    coords: Optional[List[str]] = None,
) -> sc.DataArray:
    """
    Pre-process input data for plotting.
    This involves:

      - converting the input to a data array
      - filling in missing dimension coords if needed
      - renaming dimensions if non-dimension coordinates are to be used

    Parameters
    ----------
    obj:
        The input object that will be plotted.
    name:
        Override the input's name (when a dict-like structure is to be plotted).
    ignore_size:
        Do not perform a size check on the object before plotting it.
    coords:
        If supplied, use these coords instead of the input's dimension coordinates.
    """
    out = to_data_array(obj)
    check_not_binned(out)
    check_allowed_dtypes(out)
    if name is not None:
        out.name = name
    if not ignore_size:
        _check_size(out)
    if coords is not None:
        renamed_dims = {}
        if isinstance(coords, str):
            coords = [coords]
        for dim in coords:
            underlying = out.coords[dim].dims[-1]
            renamed_dims[underlying] = dim
        out = out.rename_dims(**renamed_dims)
    for n, coord in out.coords.items():
        if (coord.ndim == 0) or (n not in out.dims):
            continue
        try:
            if not (
                _all_dims_sorted(coord, order='ascending')
                or _all_dims_sorted(coord, order='descending')
            ):
                warnings.warn(
                    'The input contains a coordinate with unsorted values '
                    f'({n}). The results may be unpredictable. '
                    'Coordinates can be sorted using '
                    '`scipp.sort(data, dim="to_be_sorted", order="ascending")`.',
                    RuntimeWarning,
                    stacklevel=2,
                )
        except sc.DTypeError:
            pass
    return out


def input_to_nodes(obj: PlottableMulti, processor: Callable) -> List[Node]:
    """
    Convert an input or dict of inputs to a list of nodes that provide pre-processed
    data.

    Parameters
    ----------
    obj:
        The input(s) to be converted to nodes.
    processor:
        The function that will be applied to each input to convert it to a node.
    """
    if hasattr(obj, 'items') and not is_pandas_series(obj):
        to_nodes = obj.items()
    else:
        to_nodes = [(None, obj)]
    nodes = [Node(processor, inp, name=name) for name, inp in to_nodes]
    for node in nodes:
        if hasattr(processor, 'func'):
            node.name = processor.func.__name__
        else:
            node.name = 'Preprocess data'
    return nodes


def raise_multiple_inputs_for_2d_plot_error(origin):
    """
    Raise an error if the user tries to plot multiple 2d data entries.

    Parameters
    ----------
    origin:
        The name of the function that called this function.
    """
    raise ValueError(
        f'The {origin} function can only plot a single 2d data entry. If you want '
        'to create multiple figures, see the documentation on subplots at '
        'https://scipp.github.io/plopp/customization/subplots.html. If you '
        'want to plot two images onto the same axes, use the lower-level '
        'plopp.figure2d function.'
    )
