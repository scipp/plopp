# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core import input_node
from .common import preprocess

import scipp as sc
from numpy import ndarray
from typing import Union, Literal


def scatter3d(obj: Union[sc.typing.VariableLike, ndarray],
              *,
              x: str = None,
              y: str = None,
              z: str = None,
              dim: str = None,
              norm: Literal['linear', 'log'] = 'linear',
              title: str = None,
              vmin: sc.Variable = None,
              vmax: sc.Variable = None,
              cmap: str = None,
              **kwargs):
    """
    """
    from ..graphics import Scene3d

    da = preprocess(obj, ignore_size=True)

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
