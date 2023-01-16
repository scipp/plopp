# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import warnings
from typing import Dict, List, Optional, Union

import numpy as np
import scipp as sc

from .. import backends
from ..core.utils import number_to_variable


def require_interactive_backend(func: str):
    """
    Raise an error if the current backend in use is non-interactive.
    """
    if not backends.is_interactive():
        raise RuntimeError(f"The {func} can only be used with an interactive backend "
                           "backend. Use `%matplotlib widget` at the start of your "
                           "notebook.")


def _to_data_array(obj: Union[np.ndarray, sc.Variable, sc.DataArray]):
    """
    Convert an input to a DataArray, potentially adding fake coordinates if they are
    missing.
    """
    out = obj
    if isinstance(out, np.ndarray):
        dims = [f"axis-{i}" for i in range(len(out.shape))]
        out = sc.Variable(dims=dims, values=out)
    if isinstance(out, sc.Variable):
        out = sc.DataArray(data=out)
    out = out.copy(deep=False)
    for dim, size in out.sizes.items():
        if dim not in out.meta:
            out.coords[dim] = sc.arange(dim, size, unit=None)
    return out


def _to_variable_if_not_none(x: sc.Variable, unit: str) -> Union[None, sc.Variable]:
    """
    Convert input to the required unit if it is not ``None``.
    """
    if x is not None:
        return number_to_variable(x, unit=unit)


def _check_size(da: sc.DataArray):
    """
    Prevent slow figure rendering by raising an error if the data array exceeds a
    default size.
    """
    limits = {1: 1_000_000, 2: 2500 * 2500}
    if da.ndim not in limits:
        raise ValueError("plot can only handle 1d and 2d data.")
    if np.prod(da.shape) > limits[da.ndim]:
        raise ValueError(f"Plotting data of size {da.shape} may take very long or use "
                         "an excessive amount of memory. This is therefore disabled by "
                         "default. To bypass this check, use `ignore_size=True`.")


def check_not_binned(obj):
    if obj.bins is not None:
        params = ', '.join([f'{dim}=100' for dim in obj.dims])
        raise ValueError(
            "Cannot plot binned data, it must be histogrammed first, "
            f"e.g., using ``obj.hist()`` or obj.hist({params})``."
            "See https://scipp.github.io/generated/functions/scipp.hist.html for "
            "more details.")


def _all_dims_sorted(var, order='ascending'):
    return all([sc.allsorted(var, dim, order=order) for dim in var.dims])


def preprocess(obj: Union[np.ndarray, sc.Variable, sc.DataArray],
               crop: Optional[Dict[str, Dict[str, sc.Variable]]] = None,
               name: str = '',
               ignore_size: bool = False,
               coords: Optional[List[str]] = None):
    """
    Pre-process input data for plotting.
    This involves:

      - converting the input to a data array
      - filling in missing dimension coords if needed
      - slicing out the parts that are not needed if cropping is requested
      - renaming dimensions if non-dimension coordinates are to be used

    Parameters
    ----------
    obj:
        The input object that will be plotted.
    crop:
        Used to define cropping. See :func:`plot` for syntax.
    name:
        Override the input's name if it has none.
    ignore_size:
        Do not perform a size check on the object before plotting it.
    coords:
        If supplied, use these coords instead of the input's dimension coordinates.
    """
    out = _to_data_array(obj)
    check_not_binned(out)
    if not out.name:
        out.name = name
    crop = {} if crop is None else crop
    for dim, sl in crop.items():
        # If we plainly slice using label values, we can miss the first and last points
        # that lie just outside the selected range, but whose pixels are still visible
        # on the figure (this mostly arises in the case of a 2d image with no bin-edge
        # coord). Therefore, we convert the value-based range to slicing indices, and
        # then extend the lower and upper bounds by 1.
        smin = _to_variable_if_not_none(sl.get('min'), unit=out.meta[dim].unit)
        smax = _to_variable_if_not_none(sl.get('max'), unit=out.meta[dim].unit)
        start = max(out[dim, :smin].sizes[dim] - 1, 0)
        width = out[dim, smin:smax].sizes[dim]
        out = out[dim, start:start + width + 2]
    if not ignore_size:
        _check_size(out)
    if coords is not None:
        renamed_dims = {}
        if isinstance(coords, str):
            coords = [coords]
        for dim in coords:
            underlying = out.meta[dim].dims[-1]
            renamed_dims[underlying] = dim
        out = out.rename_dims(**renamed_dims)
    for name, coord in out.coords.items():
        if coord.ndim > 0:
            try:
                if not (_all_dims_sorted(coord, order='ascending')
                        or _all_dims_sorted(coord, order='descending')):
                    warnings.warn(
                        'The input contains a coordinate with unsorted values '
                        f'({name}). The results may be unpredictable. '
                        'Coordinates can be sorted using '
                        '`scipp.sort(data, dim="to_be_sorted", order="ascending")`.',
                        UserWarning)
            except sc.DTypeError:
                pass
    return out
