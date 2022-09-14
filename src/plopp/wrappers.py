# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .figure import Figure
from .model import input_node
from .prep import preprocess

from scipp import Variable, Dataset
from scipp.typing import VariableLike
import inspect
from matplotlib import get_backend
from typing import Union, Dict, Literal


def figure(*args, **kwargs):
    """
    Make a figure that is either static or interactive depending on the backend in use.
    """
    if 'ipympl' in get_backend():
        from .interactive import InteractiveFig
        return InteractiveFig(*args, **kwargs)
    else:
        from .static import StaticFig
        return StaticFig(*args, **kwargs)


def plot(obj: Union[VariableLike, Dict[str, VariableLike]],
         aspect: Literal['auto', 'equal'] = 'auto',
         cbar: bool = True,
         crop: Dict[str, Dict[str, Variable]] = None,
         errorbars: bool = True,
         grid: bool = False,
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
        The object to be plotted. Possible inputs are:
        - Variable
        - Dataset
        - DataArray
        - numpy ndarray
        - dict of Variables
        - dict of DataArrays
        - dict of numpy ndarrays
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
        **{k: v
           for k, v in listed_args.items() if k not in ('obj', 'kwargs')},
        **kwargs
    }
    if isinstance(obj, (dict, Dataset)):
        nodes = [
            input_node(preprocess(item, crop=crop, name=name))
            for name, item in obj.items()
        ]
        return figure(*nodes, **all_args)
    else:
        return figure(input_node(preprocess(obj, crop=crop)), **all_args)
