# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core.utils import number_to_variable

from matplotlib import get_backend
from numpy import ndarray, prod
from scipp import Variable, DataArray, arange, to_unit


def is_interactive_backend():
    """
    Return `True` if the current backend used by Matplotlib is the widget backend.
    """
    return 'ipympl' in get_backend()


def require_interactive_backend(func):
    if not is_interactive_backend():
        raise RuntimeError(f"The {func} can only be used with the interactive widget "
                           "backend. Use `%matplotlib widget` at the start of your "
                           "notebook.")


def _to_data_array(obj):
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


def _convert_if_not_none(x, unit):
    if x is not None:
        return to_unit(number_to_variable(x), unit=unit)
    return x


def _check_size(obj):
    limits = {1: 1_000_000, 2: 2500 * 2500}
    if obj.ndim not in limits:
        raise ValueError("plot can only handle 1d and 2d data.")
    if prod(obj.shape) > limits[obj.ndim]:
        raise ValueError(f"Plotting data of size {obj.shape} may take very long or use "
                         "an excessive amount of memory. This is therefore disabled by "
                         "default. To bypass this check, use `ignore_size=True`.")


def preprocess(obj, crop=None, name='', ignore_size=False):
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
        smin = _convert_if_not_none(sl.get('min'), unit=out.meta[dim].unit)
        smax = _convert_if_not_none(sl.get('max'), unit=out.meta[dim].unit)
        start = max(out[dim, :smin].sizes[dim] - 1, 0)
        width = out[dim, smin:smax].sizes[dim]
        out = out[dim, start:start + width + 2]
    if not ignore_size:
        _check_size(out)
    return out
