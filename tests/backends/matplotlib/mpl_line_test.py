# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import numpy as np
import pytest
import scipp as sc

from plopp.backends.matplotlib.canvas import Canvas
from plopp.backends.matplotlib.line import Line
from plopp.data.testing import data_array

pytestmark = pytest.mark.usefixtures("_parametrize_mpl_backends")


def test_line_creation():
    da = data_array(ndim=1, unit='K')
    line = Line(canvas=Canvas(), data=da)
    assert line._unit == 'K'
    assert line._dim == 'xx'
    assert len(line._line.get_xdata()) == da.sizes['xx']
    assert np.allclose(line._line.get_xdata(), da.coords['xx'].values)
    assert np.allclose(line._line.get_ydata(), da.values)
    assert line._error is None
    assert not line._mask.get_visible()


def test_line_creation_bin_edges():
    da = data_array(ndim=1, binedges=True)
    line = Line(canvas=Canvas(), data=da)
    assert len(line._line.get_xdata()) == da.sizes['xx'] + 1


def test_line_with_errorbars():
    da = data_array(ndim=1, variances=True)
    line = Line(canvas=Canvas(), data=da)
    assert line._error.has_yerr
    coll = line._error.get_children()[0]
    x = np.array(coll.get_segments())[:, 0, 0]
    y1 = np.array(coll.get_segments())[:, 0, 1]
    y2 = np.array(coll.get_segments())[:, 1, 1]
    assert np.allclose(x, da.coords['xx'].values)
    assert np.allclose(y1, (da.data - sc.stddevs(da.data)).values)
    assert np.allclose(y2, (da.data + sc.stddevs(da.data)).values)


def test_line_with_bin_edges_and_errorbars():
    da = data_array(ndim=1, binedges=True, variances=True)
    line = Line(canvas=Canvas(), data=da)
    coll = line._error.get_children()[0]
    x = np.array(coll.get_segments())[:, 0, 0]
    assert np.allclose(x, sc.midpoints(da.coords['xx']).values)


def test_line_hide_errorbars():
    da = data_array(ndim=1, variances=True)
    line = Line(canvas=Canvas(), data=da, errorbars=False)
    assert line._error is None


def test_line_with_mask():
    da = data_array(ndim=1, masks=True)
    line = Line(canvas=Canvas(), data=da)
    assert line._mask.get_visible()


def test_line_with_mask_and_binedges():
    da = data_array(ndim=1, binedges=True, masks=True)
    line = Line(canvas=Canvas(), data=da)
    assert line._mask.get_visible()


def test_line_with_two_masks():
    da = data_array(ndim=1, masks=True)
    da.masks['two'] = da.coords['xx'] > sc.scalar(25, unit='m')
    line = Line(canvas=Canvas(), data=da)
    expected = da.data[da.masks['mask'] | da.masks['two']].values
    y = line._mask.get_ydata()
    assert np.allclose(y[~np.isnan(y)], expected)


def test_line_update():
    da = data_array(ndim=1)
    line = Line(canvas=Canvas(), data=da)
    assert np.allclose(line._line.get_xdata(), da.coords['xx'].values)
    assert np.allclose(line._line.get_ydata(), da.values)
    line.update(da * 2.5)
    assert np.allclose(line._line.get_xdata(), da.coords['xx'].values)
    assert np.allclose(line._line.get_ydata(), da.values * 2.5)


def test_line_update_with_errorbars():
    da = data_array(ndim=1, variances=True)
    line = Line(canvas=Canvas(), data=da)
    coll = line._error.get_children()[0]
    x = np.array(coll.get_segments())[:, 0, 0]
    y1 = np.array(coll.get_segments())[:, 0, 1]
    y2 = np.array(coll.get_segments())[:, 1, 1]
    assert np.allclose(x, da.coords['xx'].values)
    assert np.allclose(y1, (da.data - sc.stddevs(da.data)).values)
    assert np.allclose(y2, (da.data + sc.stddevs(da.data)).values)
    new_values = da * 2.5
    new_values.variances = da.variances
    line.update(new_values)
    coll = line._error.get_children()[0]
    y1 = np.array(coll.get_segments())[:, 0, 1]
    y2 = np.array(coll.get_segments())[:, 1, 1]
    assert np.allclose(y1, (da.data * 2.5 - sc.stddevs(da.data)).values)
    assert np.allclose(y2, (da.data * 2.5 + sc.stddevs(da.data)).values)


def test_line_datetime_binedges_with_errorbars():
    t = np.arange(
        np.datetime64('2017-03-16T20:58:17'), np.datetime64('2017-03-16T21:15:17'), 20
    )
    time = sc.array(dims=['time'], values=t)
    v = np.random.rand(time.sizes['time'] - 1)
    da = sc.DataArray(
        data=sc.array(dims=['time'], values=10 * v, variances=v), coords={'time': time}
    )
    # Checking for the locations of the errorbars is slightly strange, as the
    # get_segments() method from the LineCollection gives x values as floats, not
    # datetime, and comparing with the original data is thus difficult as the floats
    # do not seem immediately convertible to datetimes.
    # Hence, we simply check if the Line can be created without raising an exception.
    Line(canvas=Canvas(), data=da)


def test_line_color():
    da = data_array(ndim=1)
    line = Line(canvas=Canvas(), data=da, color='red')
    assert line.color == 'red'
    assert line._line.get_color() == 'red'
    line.color = 'blue'
    assert line.color == 'blue'
    assert line._line.get_color() == 'blue'


def test_kwarg_linestyle():
    da = data_array(ndim=1)
    line = Line(canvas=Canvas(), data=da, linestyle='solid')
    assert line._line.get_linestyle() == '-'
    line = Line(canvas=Canvas(), data=da, ls='dashed')
    assert line._line.get_linestyle() == '--'


def test_kwarg_linewidth():
    da = data_array(ndim=1)
    line = Line(canvas=Canvas(), data=da, linewidth=3)
    assert line._line.get_linewidth() == 3
    line = Line(canvas=Canvas(), data=da, lw=5)
    assert line._line.get_linewidth() == 5


def test_kwarg_marker():
    da = data_array(ndim=1)
    line = Line(canvas=Canvas(), data=da, marker='+')
    assert line._line.get_marker() == '+'


def test_line_color_with_errorbars():
    from matplotlib.colors import to_hex

    da = data_array(ndim=1, variances=True)
    line = Line(canvas=Canvas(), data=da, color='C0')
    assert line.color == 'C0'
    assert line._line.get_color() == 'C0'
    assert to_hex(line._error.get_children()[0].get_color()) == to_hex('C0')
    line.color = 'C1'
    assert line.color == 'C1'
    assert line._line.get_color() == 'C1'
    assert to_hex(line._error.get_children()[0].get_color()) == to_hex('C1')


def test_kwarg_zorder():
    line = Line(canvas=Canvas(), data=data_array(ndim=1), zorder=3)
    assert line._line.get_zorder() == 3


def test_kwarg_zorder_masks():
    line = Line(canvas=Canvas(), data=data_array(ndim=1, masks=True), zorder=5)
    assert line._line.get_zorder() == 5
    assert line._mask.get_zorder() > 5


def test_kwarg_zorder_binedges():
    line = Line(canvas=Canvas(), data=data_array(ndim=1, binedges=True), zorder=7)
    assert line._line.get_zorder() == 7


def test_kwarg_zorder_binedges_masks():
    line = Line(
        canvas=Canvas(), data=data_array(ndim=1, binedges=True, masks=True), zorder=9
    )
    assert line._line.get_zorder() == 9
    assert line._mask.get_zorder() < 9


def test_kwarg_zorder_errorbars():
    line = Line(canvas=Canvas(), data=data_array(ndim=1, variances=True), zorder=12)
    assert line._line.get_zorder() == 12
    for artist in line._error.get_children():
        assert artist.get_zorder() == 12


def test_kwarg_zorder_binedges_errorbars():
    line = Line(
        canvas=Canvas(),
        data=data_array(ndim=1, binedges=True, variances=True),
        zorder=14,
    )
    assert line._line.get_zorder() == 14
    for artist in line._error.get_children():
        assert artist.get_zorder() == 14
