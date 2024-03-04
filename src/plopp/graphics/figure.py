# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import warnings
from typing import Literal

from .. import backends
from ..core.typing import VisibleDeprecationWarning


def _warn_deprecated(func_name: str, new_func_name: str):
    warnings.warn(
        f'The function `{func_name}` is deprecated and will be removed in a future '
        f'version. Use `{new_func_name}` instead.',
        VisibleDeprecationWarning,
        stacklevel=2,
    )


def figure1d(*args, style: Literal['line'] = 'line', **kwargs):
    """
    Create a figure to represent one-dimensional data from one or more graph node(s).
    By default, this will return a figure built from :class:`LineView` (see the
    documentation of this class for a list of available customization arguments).

    .. deprecated:: v24.03.0

    Parameters
    ----------
    style:
        The type of figure to create.

    Examples
    --------
    Create an input node and attach a figure1d as a view:

      >>> da = pp.data.data1d()
      >>> in_node = pp.Node(da)
      >>> fig = pp.figure1d(in_node)

    Visualize two data arrays on the same figure:

      >>> a = pp.data.data1d()
      >>> b = 3 * a
      >>> a_node = pp.Node(a)
      >>> b_node = pp.Node(b)
      >>> fig = pp.figure1d(a_node, b_node)

    With a customization argument to make the vertical scale logarithmic:

      >>> da = pp.data.data1d()
      >>> in_node = pp.Node(da)
      >>> fig = pp.figure1d(in_node, norm='log')
    """

    _warn_deprecated('figure1d', 'linefigure')

    if style == 'line':
        from .lineview import LineView

        return backends.figure1d(LineView, *args, **kwargs)

    raise ValueError(f'Unsupported style={style} for figure1d.')


def figure2d(*args, style: Literal['image'] = 'image', **kwargs):
    """
    Create a figure to represent two-dimensional data from a graph node.
    By default, this will return a figure built from :class:`ImageView` (see the
    documentation of this class for a list of available customization arguments).

    .. deprecated:: v24.03.0

    Parameters
    ----------
    style:
        The type of figure to create.

    Examples
    --------
    Create an input node and attach a figure2d as a view:

      >>> da = pp.data.data2d()
      >>> in_node = pp.Node(da)
      >>> fig = pp.figure2d(in_node)

    With a customization argument to make the color scale logarithmic:

      >>> da = pp.data.data2d()
      >>> in_node = pp.Node(da)
      >>> fig = pp.figure2d(in_node, norm='log')
    """

    _warn_deprecated('figure2d', 'imagefigure')

    if style == 'image':
        from .imageview import ImageView

        return backends.figure2d(ImageView, *args, **kwargs)

    raise ValueError(f'Unsupported style={style} for figure2d.')


def figure3d(*args, style: Literal['scatter'] = 'scatter', **kwargs):
    """
    Create a figure to represent three-dimensional data from a graph node.
    By default, this will return a figure built from :class:`FigScatter3d` (see the
    documentation of this class for a list of available customization arguments).

    .. deprecated:: v24.03.0

    Parameters
    ----------
    style:
        The type of figure to create.

    Examples
    --------
    Create an input node and attach a figure3d as a view:

      >>> da = pp.data.scatter()
      >>> in_node = pp.Node(da)
      >>> fig = pp.figure3d(in_node)

    With a customization argument to make the color scale logarithmic:

      >>> da = pp.data.scatter()
      >>> in_node = pp.Node(da)
      >>> fig = pp.figure3d(in_node, norm='log')
    """

    _warn_deprecated('figure3d', 'scatter3dfigure')

    if style == 'scatter':
        from .scatter3dview import Scatter3dView

        return backends.figure3d(Scatter3dView, *args, **kwargs)

    raise ValueError(f'Unsupported style={style} for figure3d.')
