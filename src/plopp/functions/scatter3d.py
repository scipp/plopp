# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core import input_node

import scipp as sc
from typing import Union, Literal, Tuple


def scatter3d(da: sc.DataArray,
              *,
              x: str = None,
              y: str = None,
              z: str = None,
              dim: str = None,
              figsize: Tuple[Union[int, float]] = None,
              norm: Literal['linear', 'log'] = 'linear',
              title: str = None,
              vmin: sc.Variable = None,
              vmax: sc.Variable = None,
              cmap: str = 'viridis',
              **kwargs):
    """Make a three-dimensional scatter plot.

    To specify the positions of the scatter points, you can use:

    - a single coordinate inside the supplied data array that has dtype ``vector3``
      (use the ``dim`` parameter to specify the name of the coordinate).
    - three coordinates from the data array, whose names are specified using the
      ``x``, ``y``, and ``z`` arguments.

    Note that if ``dim`` is used, ``x``, ``y``, and ``z`` must all be ``None``.

    Parameters
    ----------
    da:
        The data array containing the data and the coordinates.
    x:
        The name of the coordinate that is to be used for the X positions.
    y:
        The name of the coordinate that is to be used for the Y positions.
    z:
        The name of the coordinate that is to be used for the Z positions.
    dim:
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
    from ..graphics import Scene3d

    if dim is not None:
        if any((x, y, z)):
            raise ValueError(f'If dim ({dim}) is defined, all of '
                             f'x ({x}), y ({y}), and z ({z}) must be None.')
        coords = {
            (x := f'{dim}.x'): da.meta[dim].fields.x,
            (y := f'{dim}.y'): da.meta[dim].fields.y,
            (z := f'{dim}.z'): da.meta[dim].fields.z
        }
    else:
        coords = {k: da.meta[k] for k in (x, y, z)}

    return Scene3d(input_node(sc.DataArray(data=da.data, masks=da.masks,
                                           coords=coords)),
                   x=x,
                   y=y,
                   z=z,
                   norm=norm,
                   title=title,
                   vmin=vmin,
                   vmax=vmax,
                   cmap=cmap,
                   **kwargs)
