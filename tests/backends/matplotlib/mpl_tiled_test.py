# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import pytest
import scipp as sc

from plopp.backends.matplotlib.tiled import Tiled
from plopp.data.testing import data_array

pytestmark = pytest.mark.usefixtures("_parametrize_mpl_backends")


def test_copy():
    da = data_array(ndim=1)
    original = da.plot()
    copy = original.copy()
    assert original.graph_nodes.keys() == copy.graph_nodes.keys()
    assert original.artists.keys() == copy.artists.keys()


def test_copy_keeps_kwargs():
    da = data_array(ndim=1)
    original = da.plot(
        scale={'xx': 'log'},
        norm='log',
        grid=True,
        title='A nice title',
    )
    copy = original.copy()
    assert copy.canvas.xscale == 'log'
    assert copy.canvas.yscale == 'log'
    assert copy.canvas.grid
    assert copy.canvas.title == 'A nice title'


def test_side_by_side():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=2)
    tiled = Tiled(nrows=1, ncols=2)
    tiled[0, 0] = da1.plot()
    tiled[0, 1] = da2.plot()
    assert tiled.nrows == 1
    assert tiled.ncols == 2


def test_top_bottom():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=2)
    tiled = Tiled(nrows=2, ncols=1)
    tiled[0, 0] = da1.plot()
    tiled[1, 0] = da2.plot()
    assert tiled.nrows == 2
    assert tiled.ncols == 1


def test_grid():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=2)
    tiled = Tiled(nrows=2, ncols=2)
    tiled[0, 0] = da1.plot()
    tiled[0, 1] = da2.plot()
    tiled[1, 0] = da1.plot()
    tiled[1, 1] = da2.plot()
    assert tiled.nrows == 2
    assert tiled.ncols == 2


def test_range():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=2)
    tiled = Tiled(nrows=1, ncols=3)
    tiled[0, :2] = da1.plot()
    tiled[0, 2] = da2.plot()
    assert tiled.nrows == 1
    assert tiled.ncols == 3


def test_add():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=2)
    da3 = data_array(ndim=1, binedges=True)
    da4 = data_array(ndim=2, binedges=True)
    tiled1 = Tiled(nrows=1, ncols=2)
    tiled1[0, 0] = da1.plot()
    tiled1[0, 1] = da2.plot()
    tiled2 = Tiled(nrows=1, ncols=2)
    tiled2[0, 0] = da3.plot()
    tiled2[0, 1] = da4.plot()
    tiled = tiled1 + tiled2
    assert tiled.nrows == 1
    assert tiled.ncols == 4


def test_add_tiled_figure():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=2)
    da3 = data_array(ndim=1, binedges=True)
    tiled1 = Tiled(nrows=1, ncols=2)
    tiled1[0, 0] = da1.plot()
    tiled1[0, 1] = da2.plot()
    tiled = tiled1 + da3.plot()
    assert tiled.nrows == 1
    assert tiled.ncols == 3


def test_add_figure_tiled():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=2)
    da3 = data_array(ndim=1, binedges=True)
    tiled1 = Tiled(nrows=1, ncols=2)
    tiled1[0, 0] = da1.plot()
    tiled1[0, 1] = da2.plot()
    tiled = da3.plot() + tiled1
    assert tiled.nrows == 1
    assert tiled.ncols == 3


def test_divide():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=2)
    da3 = data_array(ndim=1, binedges=True)
    da4 = data_array(ndim=2, binedges=True)
    tiled1 = Tiled(nrows=1, ncols=2)
    tiled1[0, 0] = da1.plot()
    tiled1[0, 1] = da2.plot()
    tiled2 = Tiled(nrows=1, ncols=2)
    tiled2[0, 0] = da3.plot()
    tiled2[0, 1] = da4.plot()
    tiled = tiled1 / tiled2
    assert tiled.nrows == 2
    assert tiled.ncols == 2


def test_divide_tiled_figure():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=2)
    da3 = data_array(ndim=1, binedges=True)
    da4 = data_array(ndim=2, binedges=True)
    tiled1 = Tiled(nrows=1, ncols=3)
    tiled1[0, 0] = da1.plot()
    tiled1[0, 1] = da2.plot()
    tiled1[0, 2] = da3.plot()
    tiled = tiled1 / da4.plot()
    assert tiled.nrows == 2
    assert tiled.ncols == 3


def test_divide_figure_tiled():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=2)
    da3 = data_array(ndim=1, binedges=True)
    da4 = data_array(ndim=2, binedges=True)
    tiled1 = Tiled(nrows=1, ncols=3)
    tiled1[0, 0] = da1.plot()
    tiled1[0, 1] = da2.plot()
    tiled1[0, 2] = da3.plot()
    tiled = da4.plot() / tiled1
    assert tiled.nrows == 2
    assert tiled.ncols == 3


def test_figure_add():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=2)
    tiled = da1.plot() + da2.plot()
    assert tiled.nrows == 1
    assert tiled.ncols == 2


def test_figure_divide():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=2)
    tiled = da1.plot() / da2.plot()
    assert tiled.nrows == 2
    assert tiled.ncols == 1


def test_figure_operators():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=2)
    da3 = data_array(ndim=1, binedges=True)
    da4 = data_array(ndim=2, binedges=True)
    tiled = (da1.plot() + da2.plot()) / (da3.plot() + da4.plot())
    assert tiled.nrows == 2
    assert tiled.ncols == 2


def test_tiled_keeps_figure_kwargs():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=1) * 3.3
    p1 = da1.plot(grid=True, title="My Title", vmin=-2.3, vmax=10)
    p2 = da2.plot(norm='log')
    tiled = p1 + p2
    assert tiled[0, 0].canvas.grid
    assert tiled[0, 0].canvas.title == "My Title"
    assert tiled[0, 0].canvas.ymin == -2.3
    assert tiled[0, 0].canvas.ymax == 10
    assert tiled[0, 1].canvas.yscale == 'log'


def test_tiled_keeps_figure_props():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=1) * 3.3
    p1 = da1.plot()
    p2 = da2.plot()
    p1.canvas.yscale = "log"
    p2.canvas.xscale = "log"
    tiled = p1 + p2
    assert tiled[0, 0].canvas.xscale == 'linear'
    assert tiled[0, 0].canvas.yscale == 'log'
    assert tiled[0, 1].canvas.xscale == 'log'
    assert tiled[0, 1].canvas.yscale == 'linear'


def test_tiled_keeps_aspect():
    a = data_array(ndim=2)
    f1 = a.plot(aspect='equal')
    f2 = a.plot(cbar=False)
    tiled = f1 + f2
    assert tiled.fig.get_axes()[0].get_aspect() == 1.0
    assert tiled.fig.get_axes()[2].get_aspect() == "auto"


def _xticklabels_visible(fig) -> bool:
    return any(label.get_visible() for label in fig.ax.get_xticklabels())


def _yticklabels_visible(fig) -> bool:
    return any(label.get_visible() for label in fig.ax.get_yticklabels())


def test_sharex_gives_all_tiles_the_union_of_the_ranges():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=1)
    da2.coords['xx'] = da2.coords['xx'] + sc.scalar(100.0, unit='m')
    tiled = Tiled(nrows=2, ncols=1, sharex=True)
    tiled[0, 0] = da1.plot()
    tiled[1, 0] = da2.plot()
    expected = (
        min(da1.coords['xx'].min().value, da2.coords['xx'].min().value),
        max(da1.coords['xx'].max().value, da2.coords['xx'].max().value),
    )
    for inds in ((0, 0), (1, 0)):
        xrange = tiled[inds].canvas.xrange
        assert xrange[0] <= expected[0]
        assert xrange[1] >= expected[1]
    assert tiled[0, 0].canvas.xrange == tiled[1, 0].canvas.xrange


def test_sharex_all_keeps_x_labels_on_bottom_row_only():
    da = data_array(ndim=1)
    tiled = Tiled(nrows=2, ncols=2, sharex=True)
    for i in range(2):
        for j in range(2):
            tiled[i, j] = da.plot()
    for j in range(2):
        assert tiled[0, j].canvas.xlabel == ''
        assert not _xticklabels_visible(tiled[0, j])
        assert tiled[1, j].canvas.xlabel != ''
        assert _xticklabels_visible(tiled[1, j])


def test_sharey_all_keeps_y_labels_on_left_column_only():
    da = data_array(ndim=1)
    tiled = Tiled(nrows=2, ncols=2, sharey=True)
    for i in range(2):
        for j in range(2):
            tiled[i, j] = da.plot()
    for i in range(2):
        assert tiled[i, 0].canvas.ylabel != ''
        assert _yticklabels_visible(tiled[i, 0])
        assert tiled[i, 1].canvas.ylabel == ''
        assert not _yticklabels_visible(tiled[i, 1])


def test_sharey_col_shares_within_columns_and_keeps_all_y_labels():
    da1 = data_array(ndim=1)
    da2 = da1 * 10.0
    tiled = Tiled(nrows=2, ncols=2, sharey='col')
    for i in range(2):
        tiled[i, 0] = da1.plot()
        tiled[i, 1] = da2.plot()
    assert tiled[0, 0].canvas.yrange == tiled[1, 0].canvas.yrange
    assert tiled[0, 1].canvas.yrange == tiled[1, 1].canvas.yrange
    assert tiled[0, 0].canvas.yrange != tiled[0, 1].canvas.yrange
    for i in range(2):
        for j in range(2):
            assert tiled[i, j].canvas.ylabel != ''
            assert _yticklabels_visible(tiled[i, j])


def test_sharex_row_keeps_x_labels_on_all_rows():
    da = data_array(ndim=1)
    tiled = Tiled(nrows=2, ncols=2, sharex='row')
    for i in range(2):
        for j in range(2):
            tiled[i, j] = da.plot()
    for i in range(2):
        for j in range(2):
            assert tiled[i, j].canvas.xlabel != ''
            assert _xticklabels_visible(tiled[i, j])


def test_share_raises_for_mismatching_unit():
    da = data_array(ndim=1)
    tiled = Tiled(nrows=1, ncols=2, sharey=True)
    tiled[0, 0] = da.plot()
    with pytest.raises(ValueError, match='unit'):
        tiled[0, 1] = (da * sc.scalar(1.0, unit='K')).plot()


def test_share_raises_for_mismatching_dim():
    tiled = Tiled(nrows=1, ncols=2, sharex=True)
    tiled[0, 0] = data_array(ndim=1).plot()
    with pytest.raises(ValueError, match='dim'):
        tiled[0, 1] = data_array(ndim=1).transpose(['xx']).rename(xx='tt').plot()


def test_share_raises_for_mismatching_scale():
    da = data_array(ndim=1)
    tiled = Tiled(nrows=1, ncols=2, sharey=True)
    tiled[0, 0] = da.plot()
    with pytest.raises(ValueError, match='scale'):
        tiled[0, 1] = da.plot(norm='log')


def test_share_does_not_constrain_tiles_in_different_groups():
    da = data_array(ndim=1)
    tiled = Tiled(nrows=1, ncols=2, sharey='col')
    tiled[0, 0] = da.plot()
    tiled[0, 1] = (da * sc.scalar(1.0, unit='K')).plot()
    assert tiled[0, 1].canvas.units['data'] == sc.Unit('K') * da.unit


def test_share_raises_for_invalid_mode():
    with pytest.raises(ValueError, match='sharex'):
        Tiled(nrows=1, ncols=2, sharex='both')


def test_sharing_points_ticks_inwards_on_the_shared_axis_only():
    da = data_array(ndim=1)
    tiled = Tiled(nrows=2, ncols=2, sharey=True)
    for i in range(2):
        for j in range(2):
            tiled[i, j] = da.plot()
    for i in range(2):
        for j in range(2):
            ax = tiled[i, j].ax
            assert ax.yaxis.get_tick_params()['direction'] == 'in'
            assert 'direction' not in ax.xaxis.get_tick_params()


def test_sharing_without_dropping_labels_keeps_ticks_outwards():
    da = data_array(ndim=1)
    tiled = Tiled(nrows=2, ncols=2, sharey='col')
    for i in range(2):
        for j in range(2):
            tiled[i, j] = da.plot()
    for i in range(2):
        for j in range(2):
            assert 'direction' not in tiled[i, j].ax.yaxis.get_tick_params()


def _lay_out(tiled: Tiled) -> None:
    """Run the layout engine so that positions and extents can be measured."""
    tiled.fig.draw_without_rendering()


def test_tiles_without_inner_decorations_are_flush():
    da = data_array(ndim=1)
    tiled = Tiled(nrows=2, ncols=2, sharex=True, sharey=True)
    for i in range(2):
        for j in range(2):
            tiled[i, j] = da.plot()
    _lay_out(tiled)
    top, bottom = tiled[0, 0].ax.get_position(), tiled[1, 0].ax.get_position()
    left, right = tiled[0, 0].ax.get_position(), tiled[0, 1].ax.get_position()
    assert top.y0 == pytest.approx(bottom.y1)
    assert left.x1 == pytest.approx(right.x0)


def _shared_pair():
    da = data_array(ndim=1)
    tiled = Tiled(nrows=1, ncols=2, sharex=True, sharey=True)
    tiled[0, 0] = da.plot()
    tiled[0, 1] = (da * 2.0).plot()
    return tiled


def test_operators_do_not_propagate_sharing():
    combined = _shared_pair() + _shared_pair()
    assert combined.ncols == 4
    for j in range(4):
        assert combined[0, j].canvas.xlabel != ''
        assert _xticklabels_visible(combined[0, j])
    assert (
        not combined[0, 0]
        .ax.get_shared_x_axes()
        .joined(combined[0, 0].ax, combined[0, 1].ax)
    )


def test_divide_does_not_propagate_sharing():
    combined = _shared_pair() / _shared_pair()
    assert (combined.nrows, combined.ncols) == (2, 2)
    for i in range(2):
        assert combined[i, 0].canvas.ylabel != ''
        assert _yticklabels_visible(combined[i, 0])


def test_operators_can_combine_shared_tiles_with_incompatible_ones():
    da = data_array(ndim=1)
    other = Tiled(nrows=1, ncols=1)
    other[0, 0] = (da * sc.scalar(1.0, unit='K')).plot()
    combined = _shared_pair() + other
    assert combined.ncols == 3


def test_sharing_applies_to_tiles_spanning_several_cells():
    da = data_array(ndim=1)
    tiled = Tiled(nrows=2, ncols=2, sharex=True, sharey=True)
    tiled[0, :] = da.plot()
    tiled[1, 0] = (da * 2.0).plot()
    tiled[1, 1] = da.plot()
    assert tiled[0, 0].canvas.xlabel == ''
    assert not _xticklabels_visible(tiled[0, 0])
    assert tiled[1, 0].canvas.xlabel != ''
    assert tiled[0, 0].canvas.yrange == tiled[1, 0].canvas.yrange


def test_replacing_a_tile_raises_when_axes_are_shared():
    da = data_array(ndim=1)
    tiled = Tiled(nrows=1, ncols=2, sharey=True)
    tiled[0, 0] = da.plot()
    with pytest.raises(ValueError, match='un-share'):
        tiled[0, 0] = da.plot()


def test_replacing_a_tile_is_allowed_without_sharing():
    da = data_array(ndim=1)
    tiled = Tiled(nrows=1, ncols=2)
    tiled[0, 0] = da.plot()
    tiled[0, 0] = (da * 2.0).plot()
    assert tiled[0, 0].canvas.yrange[1] > da.max().value
