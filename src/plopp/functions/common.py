# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core.utils import number_to_variable

from matplotlib import get_backend
from numpy import ndarray, prod
from scipp import Variable, DataArray, arange
from typing import Dict, Union


def is_interactive_backend():
    """
    Return `True` if the current backend used by Matplotlib is the widget backend.
    """
    return 'ipympl' in get_backend()


def require_interactive_backend(func: str):
    """
    Raise an error if the current backend in use is non-interactive.
    """
    if not is_interactive_backend():
        raise RuntimeError(f"The {func} can only be used with the interactive widget "
                           "backend. Use `%matplotlib widget` at the start of your "
                           "notebook.")


def _to_data_array(obj: Union[ndarray, Variable, DataArray]):
    """
    Convert an input to a DataArray, potentially adding fake coordinates if they are
    missing.
    """
    out = obj
    if isinstance(out, ndarray):
        dims = [f"axis-{i}" for i in range(len(out.shape))]
        out = Variable(dims=dims, values=out)
    if isinstance(out, Variable):
        out = DataArray(data=out)
    out = out.copy(deep=False)
    for dim, size in out.sizes.items():
        if dim not in out.meta:
            out.coords[dim] = arange(dim, size, unit=None)
    return out


def _to_variable_if_not_none(x: Variable, unit: str) -> Union[None, Variable]:
    """
    Convert input to the required unit if it is not ``None``.
    """
    if x is not None:
        return number_to_variable(x, unit=unit)


def _check_size(da: DataArray):
    """
    Prevent slow figure rendering by raising an error if the data array exceeds a
    default size.
    """
    limits = {1: 1_000_000, 2: 2500 * 2500}
    if da.ndim not in limits:
        raise ValueError("plot can only handle 1d and 2d data.")
    if prod(da.shape) > limits[da.ndim]:
        raise ValueError(f"Plotting data of size {da.shape} may take very long or use "
                         "an excessive amount of memory. This is therefore disabled by "
                         "default. To bypass this check, use `ignore_size=True`.")


def preprocess(obj: Union[ndarray, Variable, DataArray],
               crop: Dict[str, Dict[str, Variable]] = None,
               name: str = '',
               ignore_size: bool = False):
    """
    Pre-process input data for plotting.
    This involves:

      - converting the input to a data array
      - filling in missing dimension coords if needed
      - slicing out the parts that are not needed if cropping is requested

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
    """
    out = _to_data_array(obj)
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
    return out
