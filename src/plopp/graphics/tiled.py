# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

# from typing import Literal

from .. import backends


def tiled(nrows: int, ncols: int, **kwargs):
    """
    A tiled figure.

    Parameters
    ----------
    nrows:
        Number of rows.
    ncols:
        Number of columns.
    **kwargs:
        Additional arguments passed to :class:`Tiled`.

    Examples
    --------
    Create a tiled figure with two plots stacked vertically:

      >>> tiled = pp.tiled(2, 1)
      >>> tiled[0] = da1.plot()
      >>> tiled[1] = da2.plot()

    Create a tiled 2x2 figure:

      >>> tiled = pp.tiled(2, 2)
      >>> tiled[0, 0] = da1.plot()
      >>> tiled[0, 1] = da2.plot()
      >>> tiled[1, 0] = da3.plot()
      >>> tiled[1, 1] = da4.plot()

    Create a tiled figure with two figures side by side and the first is twice as wide:

      >>> tiled = pp.tiled(1, 3)
      >>> tiled[0, :2] = da1.plot()
      >>> tiled[0, 2] = da2.plot()

    """
    return backends.tiled(nrows=nrows, ncols=ncols, **kwargs)