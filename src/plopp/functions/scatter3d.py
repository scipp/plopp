# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import uuid
from typing import Literal, Tuple, Union

import scipp as sc

from ..core import input_node
from .common import check_not_binned


def scatter3d(da: sc.DataArray,
              *,
              x: str = None,
              y: str = None,
              z: str = None,
              pos: str = None,
              figsize: Tuple[int, int] = (600, 400),
              norm: Literal['linear', 'log'] = 'linear',
              title: str = None,
              vmin: Union[sc.Variable, int, float] = None,
              vmax: Union[sc.Variable, int, float] = None,
              cmap: str = 'viridis',
              **kwargs):
    """Make a three-dimensional scatter plot.

    To specify the positions of the scatter points, you can use:

    - a single coordinate inside the supplied data array that has dtype ``vector3``
      (use the ``pos`` parameter to specify the name of the coordinate).
    - three coordinates from the data array, whose names are specified using the
      ``x``, ``y``, and ``z`` arguments.

    Note that if ``pos`` is used, ``x``, ``y``, and ``z`` must all be ``None``.

    Parameters
    ----------
    da:
        The data array containing the data and the coordinates.
    x:
        The name of the coordinate that is to be used for the X positions.
        Default is 'x'.
    y:
        The name of the coordinate that is to be used for the Y positions.
        Default is 'y'.
    z:
        The name of the coordinate that is to be used for the Z positions.
        Default is 'z'.
    pos:
        The name of the vector coordinate that is to be used for the positions.
    norm:
        Set to ``'log'`` for a logarithmic colorscale.
    figsize:
        The size of the 3d rendering area, in pixels: ``(width, height)``.
    title:
        The figure title.
    vmin:
        Lower bound for the colorscale.
    vmax:
        Upper bound for the colorscale.
    cmap:
        The name of the colormap.

    Returns
    -------
    :
        A three-dimensional interactive scatter plot.
    """
    from ..graphics import figure3d
    from ..widgets import Box, ToggleTool, TriCutTool

    if 'ax' in kwargs:
        raise ValueError(
            'Keyword "ax" detected. Embedding 3D scatter plots inside Matplotlib axes '
            'is not supported. See '
            'https://scipp.github.io/plopp/customization/subplots.html#FAQ:-subplots-with-3D-scatter-plots'  # noqa: E501
        )

    check_not_binned(da)

    if pos is not None:
        if any((x, y, z)):
            raise ValueError(f'If pos ({pos}) is defined, all of '
                             f'x ({x}), y ({y}), and z ({z}) must be None.')
        coords = {
            (x := f'{pos}.x'): da.meta[pos].fields.x,
            (y := f'{pos}.y'): da.meta[pos].fields.y,
            (z := f'{pos}.z'): da.meta[pos].fields.z
        }
    else:
        x = x if x is not None else 'x'
        y = y if y is not None else 'y'
        z = z if z is not None else 'z'
        coords = {k: da.meta[k] for k in (x, y, z)}

    to_plot = sc.DataArray(data=da.data, masks=da.masks, coords=coords)
    if to_plot.ndim != 1:
        to_plot = to_plot.flatten(to=uuid.uuid4().hex)
    fig = figure3d(input_node(to_plot),
                   x=x,
                   y=y,
                   z=z,
                   figsize=figsize,
                   norm=norm,
                   title=title,
                   vmin=vmin,
                   vmax=vmax,
                   cmap=cmap,
                   **kwargs)
    tri_cutter = TriCutTool(fig)
    fig.toolbar['cut3d'] = ToggleTool(callback=tri_cutter.toggle_visibility,
                                      icon='cube',
                                      tooltip='Hide/show spatial cutting tool')
    return Box([fig, tri_cutter])
