# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from functools import partial
from typing import List, Optional, Union

import scipp as sc
from numpy import ndarray

from ..core import Node
from ..graphics import figure2d
from .common import input_to_nodes, preprocess


# def _make_data_array(x: sc.Variable, y: sc.Variable) -> sc.DataArray:
#     """
#     Make a data array from the supplied variables, using ``x`` as the coordinate and
#     ``y`` as the data.

#     Parameters
#     ----------
#     x:
#         The variable to use as the coordinate.
#     y:
#         The variable to use as the data.
#     """
#     return sc.DataArray(data=y, coords={x.dim: x})


def contour(
    obj: Union[sc.Variable, ndarray, list, Node],
    coords: Optional[List[str]] = None,
    ignore_size: bool = False,
    **kwargs,
):
    """ """
    nodes = input_to_nodes(
        obj, processor=partial(preprocess, ignore_size=ignore_size, coords=coords)
    )
    return figure2d(
        *nodes,
        style='contour',
        # aspect=aspect,
        # cbar=cbar,
        # **common_args,
    )
