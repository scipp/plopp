# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import warnings
from collections.abc import Callable, Iterable
from typing import Any, Literal

import numpy as np
import scipp as sc

from ..core import Node
from ..core.typing import FigureLike, Plottable, PlottableMulti


def require_interactive_figure(fig: FigureLike, func: str):
    """
    Raise an error if the figure is non-interactive.
    """
    if not fig.interactive:
        raise RuntimeError(
            f"The {func} can only be used with an interactive backend. "
            "Use `%matplotlib widget` at the start of your notebook."
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


def _maybe_to_variable(obj: Plottable | list) -> Plottable:
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


def to_data_array(obj: Plottable | list) -> sc.DataArray:
    """
    Convert an input to a DataArray.
    Returns a shallow copy of the input if it is already a DataArray.

    Parameters
    ----------
    obj:
        The input object to be converted.
    """
    if isinstance(obj, sc.DataArray):
        return obj.copy(deep=False)
    out = _maybe_to_variable(obj)
    if isinstance(out, sc.Variable):
        out = sc.DataArray(data=out)
    out = from_compatible_lib(out)
    if not isinstance(out, sc.DataArray):
        raise TypeError(f"Cannot convert input of type {type(obj)} to a DataArray.")
    return out


def check_size(da: sc.DataArray) -> None:
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


def check_not_binned(da: sc.DataArray) -> None:
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


def to_allowed_dtypes(da: sc.DataArray) -> sc.DataArray:
    """
    Currently, Plopp cannot plot data that contains vector and matrix dtypes.
    This function will raise an error if the input data type is not supported.

    We also convert boolean data to integers, as some operations downstream
    may not support boolean data types.

    Parameters
    ----------
    da:
        The data array to be plotted.
    """
    if da.shape != da.values.shape:
        raise TypeError(
            f'The input has dtype {da.dtype} which is not supported by Plopp.'
        )
    if da.dtype == bool:
        da = da.to(dtype='int32')
    return da


def _all_dims_sorted(var, order='ascending') -> bool:
    """
    Check if all dimensions of a variable are sorted in the specified order.
    This is used to ensure that the coordinates are sorted before plotting.
    """
    return all(sc.allsorted(var, dim, order=order) for dim in var.dims)


def _rename_dims_from_coords(da: sc.DataArray, coords: Iterable[str]) -> sc.DataArray:
    """
    If coordinates are provided, rename the dimensions of the data array to match the
    names of the coordinates, so that they effectively become the dimension coordinates.
    """
    renamed_dims = {}
    underlying_dims = set()
    for dim in coords:
        underlying = da.coords[dim].dims[-1]
        if underlying in underlying_dims:
            raise ValueError(
                "coords: Cannot use more than one coordinate associated with "
                f"the same underlying dimension ({underlying})."
            )
        renamed_dims[underlying] = dim
        underlying_dims.add(underlying)
    return da.rename_dims(**renamed_dims)


def _add_missing_dimension_coords(da: sc.DataArray) -> sc.DataArray:
    """
    Add missing dimension coordinates to the data array.
    If a dimension does not have a coordinate, it will be added with a range of values.
    """
    return da.assign_coords(
        {
            dim: sc.arange(dim, da.sizes[dim], unit=None)
            for dim in da.dims
            if dim not in da.coords
        }
    )


def _drop_non_dimension_coords(da: sc.DataArray) -> sc.DataArray:
    """
    Drop all coordinates that are not dimension coordinates.
    This is useful to ensure that only the coordinates that are actually used for
    plotting are kept.
    """
    return da.drop_coords([name for name in da.coords if name not in da.dims])


def _handle_coords_with_left_over_dimensions(da: sc.DataArray) -> sc.DataArray:
    """
    In some rare cases, the coordinate may have dimensions that are not present in the
    data array. This can happen for example when a 2d coord with bin edges is sliced
    along one dimension, leaving a coordinate with the other dimension, and a dimension
    of length 2 (because of the bin edges) in th sliced dimension.

    This function will handle such cases by averaging the coordinate over the left-over
    dimensions, effectively reducing the coordinate to a single value for each
    dimension that is not present in the data array.
    """
    return da.assign_coords(
        {
            name: da.coords[name].mean(
                [dim for dim in da.coords[name].dims if dim not in da.dims]
            )
            for name in da.coords
        }
    )


def _check_coord_sanity(da: sc.DataArray) -> None:
    """
    Warn if any coordinate is not sorted. This can lead to unpredictable results
    when plotting.
    Also, raise an error if any coordinate is scalar.
    """
    for name, coord in da.coords.items():
        try:
            if not (
                _all_dims_sorted(coord, order='ascending')
                or _all_dims_sorted(coord, order='descending')
            ):
                warnings.warn(
                    'The input contains a coordinate with unsorted values '
                    f'({name}). The results may be unpredictable. '
                    'Coordinates can be sorted using '
                    '`scipp.sort(data, dim="to_be_sorted", order="ascending")`.',
                    RuntimeWarning,
                    stacklevel=2,
                )
        except sc.DTypeError:
            pass

        if not coord.dims:
            raise ValueError(
                "Input data cannot be plotted: it has a scalar coordinate along "
                f"dimension {name}. Consider dropping this coordinate before plotting. "
                f"Use ``data.drop_coords('{name}').plot()``."
            )


def preprocess(
    obj: Plottable | list,
    name: str | None = None,
    ignore_size: bool = False,
    coords: Iterable[str] | str | None = None,
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
    if isinstance(coords, str):
        coords = [coords]
    elif coords is not None:
        coords = list(coords)

    out = to_data_array(obj)
    check_not_binned(out)
    out = to_allowed_dtypes(out)
    if name is not None:
        out.name = str(name)
    if not ignore_size:
        check_size(out)
    if coords is not None:
        out = _rename_dims_from_coords(out, coords)
    out = _add_missing_dimension_coords(out)
    out = _drop_non_dimension_coords(out)
    out = _handle_coords_with_left_over_dimensions(out)
    _check_coord_sanity(out)
    return out


def input_to_nodes(obj: PlottableMulti, processor: Callable) -> list[Node]:
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
        to_nodes = [(getattr(obj, "name", None), obj)]
    nodes = [Node(processor, inp, name=str(name)) for name, inp in to_nodes]
    for node in nodes:
        if hasattr(processor, 'func'):
            node.pretty_name = processor.func.__name__
        else:
            node.pretty_name = 'Preprocess data'
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
        'plopp.imagefigure function.'
    )


def categorize_args(
    aspect: Literal['auto', 'equal', None] = None,
    autoscale: bool = True,
    cbar: bool = True,
    clabel: str | None = None,
    cmap: str = 'viridis',
    cmax: sc.Variable | float | None = None,
    cmin: sc.Variable | float | None = None,
    errorbars: bool = True,
    figsize: tuple[float, float] | None = None,
    grid: bool = False,
    legend: bool | tuple[float, float] = True,
    logc: bool | None = None,
    logx: bool | None = None,
    logy: bool | None = None,
    mask_cmap: str = 'gray',
    mask_color: str = 'black',
    nan_color: str | None = None,
    norm: Literal['linear', 'log', None] = None,
    scale: dict[str, str] | None = None,
    title: str | None = None,
    vmax: sc.Variable | float | None = None,
    vmin: sc.Variable | float | None = None,
    xlabel: str | None = None,
    xmax: sc.Variable | float | None = None,
    xmin: sc.Variable | float | None = None,
    ylabel: str | None = None,
    ymax: sc.Variable | float | None = None,
    ymin: sc.Variable | float | None = None,
    **kwargs,
) -> dict:
    common_args = {
        'aspect': aspect,
        'autoscale': autoscale,
        'figsize': figsize,
        'grid': grid,
        'logx': logx,
        'logy': logy,
        'mask_color': mask_color,
        'norm': norm,
        'scale': scale,
        'title': title,
        'vmax': vmax,
        'vmin': vmin,
        'xlabel': xlabel,
        'xmax': xmax,
        'xmin': xmin,
        'ylabel': ylabel,
        'ymax': ymax,
        'ymin': ymin,
        **kwargs,
    }
    return {
        "1d": {'errorbars': errorbars, 'legend': legend, **common_args},
        "2d": {
            'cbar': cbar,
            'cmap': cmap,
            'cmin': cmin,
            'cmax': cmax,
            'clabel': clabel,
            'logc': logc,
            'nan_color': nan_color,
            'mask_cmap': mask_cmap,
            **common_args,
        },
    }
