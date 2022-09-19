# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .figure import Figure
from .model import input_node, widget_node
from .plot import Plot
from .prep import preprocess

from scipp import Variable, Dataset
from scipp.typing import VariableLike
import inspect
from matplotlib import get_backend
from numpy import ndarray
from typing import Union, Dict, Literal, List


def _is_interactive_backend():
    """
    Return `True` if the current backend used by Matplotlib is the widget backend.
    """
    return 'ipympl' in get_backend()


def figure(*args, **kwargs):
    """
    Make a figure that is either static or interactive depending on the backend in use.
    """
    if _is_interactive_backend():
        from .interactive import InteractiveFig
        return InteractiveFig(*args, **kwargs)
    else:
        from .static import StaticFig
        return StaticFig(*args, **kwargs)


def plot(obj: Union[VariableLike, ndarray, Dict[str, Union[VariableLike, ndarray]]],
         aspect: Literal['auto', 'equal'] = 'auto',
         cbar: bool = True,
         crop: Dict[str, Dict[str, Variable]] = None,
         errorbars: bool = True,
         grid: bool = False,
         ignore_size: bool = False,
         mask_color: str = 'black',
         norm: Literal['linear', 'log'] = 'linear',
         scale: Dict[str, str] = None,
         title: str = None,
         vmin: Variable = None,
         vmax: Variable = None,
         **kwargs) -> Figure:
    """Plot a Scipp object.

    Parameters
    ----------
    obj:
        The object to be plotted.
    aspect:
        Aspect ratio for the axes.
    cbar:
        Show colorbar in 2d plots if `True`.
    crop:
        Set the axis limits. Limits should be given as a dict with one entry per
        dimension to be cropped. Each entry should be a nested dict containing scalar
        values for `'min'` and/or `'max'`. Example:
        `da.plot(crop={'time': {'min': 2 * sc.Unit('s'), 'max': 40 * sc.Unit('s')}})`
    errorbars:
        Show errorbars in 1d plots if `True`.
    grid:
        Show grid if `True`.
    ignore_size:
        If `True`, skip the check that prevents the rendering of very large data
        objects.
    mask_color:
        Color of masks in 1d plots.
    norm:
        Set to 'log' for a logarithmic y-axis (1d plots) or logarithmic colorscale
        (2d plots).
    scale:
        Change axis scaling between `log` and `linear`. For example, specify
        `scale={'tof': 'log'}` if you want log-scale for the `tof` dimension.
    title:
        The figure title.
    vmin:
        Lower bound for data to be displayed (y-axis for 1d plots, colorscale for
        2d plots).
    vmax:
        Upper bound for data to be displayed (y-axis for 1d plots, colorscale for
        2d plots).
    **kwargs:
        All other kwargs are directly forwarded to Matplotlib, the underlying plotting
        library. The underlying functions called are the following:
        - 1d data with a non bin-edge coordinate: `plot`
        - 1d data with a bin-edge coordinate: `step`
        - 2d data: `pcolormesh`

    Returns
    -------
    :
        A figure.
    """
    _, _, _, listed_args = inspect.getargvalues(inspect.currentframe())
    all_args = {
        **{
            k: v
            for k, v in listed_args.items() if k not in ('obj', 'ignore_size', 'kwargs')
        },
        **kwargs
    }
    if isinstance(obj, (dict, Dataset)):
        nodes = [
            input_node(preprocess(item, crop=crop, name=name, ignore_size=ignore_size))
            for name, item in obj.items()
        ]
        return figure(*nodes, **all_args)
    else:
        return figure(input_node(preprocess(obj, crop=crop, ignore_size=ignore_size)),
                      **all_args)


def slicer(obj: Union[VariableLike, ndarray],
           keep: List[str] = None,
           *,
           crop: Dict[str, Dict[str, Variable]] = None,
           **kwargs) -> Plot:
    """
    Plot a multi-dimensional object by slicing one or more of the dimensions.
    This will produce one slider per sliced dimension, below the figure.

    Parameters
    ----------
    obj:
        The object to be plotted.
    keep:
        The dimensions to be kept, all remaining dimensions will be sliced. This should
        be a list of dims. If no dims are provided, the last dim will be kept in the
        case of a 2-dimensional input, while the last two dims will be kept in the case
        of higher dimensional inputs.
    crop:
        Set the axis limits. Limits should be given as a dict with one entry per
        dimension to be cropped. Each entry should be a nested dict containing scalar
        values for `'min'` and/or `'max'`. Example:
        `da.plot(crop={'time': {'min': 2 * sc.Unit('s'), 'max': 40 * sc.Unit('s')}})`
    **kwargs:
        See :py:func:`plopp.plot` for the full list of figure customization arguments.

    Returns
    -------
    :
        A :class:`Plot` which will contain a :class:`Figure` and slider widgets.
    """
    if not _is_interactive_backend():
        raise RuntimeError("The slicer can only be used with the interactive widget "
                           "backend. Use `%matplotlib widget` at the start of your "
                           "notebook.")
    from plopp.widgets import SliceWidget, slice_dims
    da = preprocess(obj, crop=crop, ignore_size=True)
    a = input_node(da)

    if keep is None:
        keep = da.dims[-(2 if da.ndim > 2 else 1):]
    sl = SliceWidget(da, dims=list(set(da.dims) - set(keep)))
    w = widget_node(sl)
    slice_node = slice_dims(a, w)
    fig = figure(slice_node, **{**{'crop': crop}, **kwargs})
    return Plot([fig, sl])
