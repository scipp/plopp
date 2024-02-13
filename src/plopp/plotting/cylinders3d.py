# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import uuid
from functools import partial
from typing import Dict, Literal, Optional, Tuple, Union

import scipp as sc

from ..core.typing import PlottableMulti
from scipp import Variable, DataGroup
from ..graphics import Camera
from .common import check_not_binned, from_compatible_lib, input_to_nodes


def _to_variable(
    var: Union[str, sc.Variable], coords: Dict[str, sc.Variable]
) -> sc.Variable:
    return coords[var] if isinstance(var, str) else var


def _preprocess_cylinders(
    obj,
    name: Optional[str] = None,
) -> sc.DataArray:
    from scipp import DType
    da = from_compatible_lib(obj['data'])
    cylinders = obj['cylinders']
    vertices = obj['vertices']

    if isinstance(da, Variable):
        da = sc.DataArray(data=da)

    # check dimensional consistency
    assert da.data.ndim == 1
    data_dim = da.data.dims[0]
    data_shape = da.data.shape[0]
    assert cylinders.ndim == 2
    assert cylinders.shape[1] == 3
    cylinder_dim = cylinders.dims[1]
    assert cylinders.shape[0] == data_shape
    assert vertices.dtype == DType.vector3
    assert cylinders.max().value < vertices.shape[0]

    base_vertices = vertices[cylinders[cylinder_dim, 0].values].flatten(to=data_dim)
    edge_vertices = vertices[cylinders[cylinder_dim, 1].values].flatten(to=data_dim)
    far_vertices = vertices[cylinders[cylinder_dim, 2].values].flatten(to=data_dim)

    coords = {
        'base': base_vertices,
        'edge': edge_vertices,
        'far': far_vertices
    }

    out = sc.DataArray(data=da.data, masks=da.masks, coords=coords)
    if out.ndim != 1:
        out = out.flatten(to=uuid.uuid4().hex)
    if name is not None:
        out.name = name
    return out


def cylinders3d(
    obj: DataGroup,
    *,
    figsize: Tuple[int, int] = (600, 400),
    norm: Literal['linear', 'log'] = 'linear',
    title: str = None,
    vmin: Union[sc.Variable, int, float] = None,
    vmax: Union[sc.Variable, int, float] = None,
    cmap: str = 'viridis',
    camera: Optional[Camera] = None,
    **kwargs,
):
    """Make a three-dimensional scatter plot.

    To specify the positions of the scatter points, you can use:

    - a single coordinate inside the supplied data array that has dtype ``vector3``
      (use the ``pos`` parameter to specify the name of the coordinate).
    - three coordinates from the data array, whose names are specified using the
      ``x``, ``y``, and ``z`` arguments.

    Note that if ``pos`` is used, ``x``, ``y``, and ``z`` must all be ``None``.

    Parameters
    ----------
    obj:
        The data group containing the data, vertex coordinates, and cylinder vertex mapping.
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
    camera:
        Initial camera configuration (position, target).

    Returns
    -------
    :
        A three-dimensional interactive scatter plot.
    """
    from ..graphics import figure3d
    from ..widgets import Box, ToggleTool, TriCutTool
    from ..core import Node

    if 'ax' in kwargs:
        raise ValueError(
            'Keyword "ax" detected. Embedding 3D scatter plots inside Matplotlib axes '
            'is not supported. See '
            'https://scipp.github.io/plopp/customization/subplots.html#FAQ:-subplots-with-3D-scatter-plots'  # noqa: E501
        )

    # nodes = input_to_nodes(
    #     obj, processor=_preprocess_cylinders,
    # )

    node = Node(_preprocess_cylinders, obj, name='input')
    if hasattr(_preprocess_cylinders, 'func'):
        node.name = _preprocess_cylinders.func.__name__
    else:
        node.name = 'Preprocess data'

    fig = figure3d(
        node,
        base='base',
        edge='edge',
        far='far',
        figsize=figsize,
        norm=norm,
        title=title,
        vmin=vmin,
        vmax=vmax,
        cmap=cmap,
        camera=camera,
        style='cylinder',
        **kwargs,
    )
    tri_cutter = TriCutTool(fig)
    fig.toolbar['cut3d'] = ToggleTool(
        callback=tri_cutter.toggle_visibility,
        icon='cube',
        tooltip='Hide/show spatial cutting tool',
    )
    return Box([fig, tri_cutter])
