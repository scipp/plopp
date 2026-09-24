# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import pytest

from plopp.backends.matplotlib.tiled import Tiled
from plopp.data.testing import data_array

# Static figures only: rendering a figure as a widget replaces the constrained layout
# with a placeholder engine (see ``Canvas.to_widget``), so the padding that keeps
# decorations clear of the neighbouring tile cannot be adjusted there.
pytestmark = pytest.mark.usefixtures("_parametrize_static_mpl_backend")


def _lay_out(tiled: Tiled) -> None:
    """Run the layout engine so that positions and extents can be measured."""
    tiled.fig.draw_without_rendering()


def test_flush_tiles_leave_room_above_a_title():
    da = data_array(ndim=1)
    tiled = Tiled(nrows=2, ncols=1, sharex=True, sharey=True)
    tiled[0, 0] = da.plot(title='top')
    tiled[1, 0] = da.plot(title='bottom')
    _lay_out(tiled)
    title = tiled[1, 0].ax.title.get_window_extent()
    above = tiled[0, 0].ax.get_window_extent()
    assert title.y1 < above.y0


def test_flush_tiles_leave_room_beside_a_colorbar():
    da = data_array(ndim=2)
    tiled = Tiled(nrows=1, ncols=2, sharex=True, sharey=True)
    tiled[0, 0] = da.plot()
    tiled[0, 1] = da.plot()
    _lay_out(tiled)
    cbar = tiled[0, 0].cax.get_window_extent()
    right = tiled[0, 1].ax.get_window_extent()
    assert cbar.x1 < right.x0
