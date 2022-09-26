# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core import input_node
from .common import preprocess

from scipp import Variable, Dataset
from scipp.typing import VariableLike
from numpy import ndarray
from typing import Union, Dict, Literal


def scatter3d(obj: Union[VariableLike, ndarray],
              dim: str = 'position',
              cbar: bool = True,
              norm: Literal['linear', 'log'] = 'linear',
              title: str = None,
              vmin: Variable = None,
              vmax: Variable = None,
              cmap: str = None,
              **kwargs):
    """
    """
    from ..graphics import Scene3d
    return Scene3d(input_node(preprocess(obj, ignore_size=True)),
                   dim=dim,
                   cbar=cbar,
                   norm=norm,
                   title=title,
                   vmin=vmin,
                   vmax=vmax,
                   cmap=cmap,
                   **kwargs)
