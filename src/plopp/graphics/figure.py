# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from typing import Literal

from .. import backends


def figure1d(*args, style: Literal['line'] = 'line', **kwargs):
    """
    Create a figure to represent one-dimensional data from one or more graph node(s).
    By default, this will return a figure built from :class:`FigLine` (see the
    documentation of this class for a list of available customization arguments).

    Parameters
    ----------
    style:
        The type of figure to create.

    Examples
    --------
    Create an input node and attach a figure1d as a view:

      >>> in_node = pp.input_node(da)
      >>> fig = pp.figure1d(in_node)

    Visualize two data arrays on the same figure:

      >>> a_node = pp.input_node(a)
      >>> b_node = pp.input_node(b)
      >>> fig = pp.figure1d(a_node, b_node)

    With a customization argument to make the vertical scale logarithmic:

      >>> in_node = pp.input_node(da)
      >>> fig = pp.figure1d(in_node, norm='log')
    """

    if style == 'line':
        from .figline import FigLine

        return backends.figure1d(*args, FigConstructor=FigLine, **kwargs)

    raise ValueError(f'Unsupported style={style} for figure1d.')


def figure2d(*args, style: Literal['image'] = 'image', **kwargs):
    """
    Create a figure to represent two-dimensional data from a graph node.
    By default, this will return a figure built from :class:`FigImage` (see the
    documentation of this class for a list of available customization arguments).

    Parameters
    ----------
    style:
        The type of figure to create.

    Examples
    --------
    Create an input node and attach a figure2d as a view:

      >>> in_node = pp.input_node(da)
      >>> fig = pp.figure2d(in_node)

    With a customization argument to make the color scale logarithmic:

      >>> in_node = pp.input_node(da)
      >>> fig = pp.figure2d(in_node, norm='log')
    """

    if style == 'image':
        from .figimage import FigImage

        return backends.figure2d(*args, FigConstructor=FigImage, **kwargs)

    raise ValueError(f'Unsupported style={style} for figure2d.')


def figure3d(*args, style: Literal['scatter'] = 'scatter', **kwargs):
    """
    Create a figure to represent three-dimensional data from a graph node.
    By default, this will return a figure built from :class:`FigScatter3d` (see the
    documentation of this class for a list of available customization arguments).

    Parameters
    ----------
    style:
        The type of figure to create.

    Examples
    --------
    Create an input node and attach a figure3d as a view:

      >>> in_node = pp.input_node(da)
      >>> fig = pp.figure3d(in_node)

    With a customization argument to make the color scale logarithmic:

      >>> in_node = pp.input_node(da)
      >>> fig = pp.figure3d(in_node, norm='log')
    """

    if style == 'scatter':
        from .figscatter3d import FigScatter3d

        return backends.figure3d(*args, FigConstructor=FigScatter3d, **kwargs)

    raise ValueError(f'Unsupported style={style} for figure3d.')
