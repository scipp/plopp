# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import os
import tempfile

import numpy as np
import pytest
import scipp as sc

import plopp as pp
from plopp.data.testing import data_array, variable


def test_plot_ndarray():
    pp.plot(np.arange(50.0).reshape(5, 10))


def test_plot_ndarray_int():
    pp.plot(np.arange(50).reshape(5, 10))


def test_plot_variable():
    pp.plot(variable(ndim=2))


def test_plot_data_array():
    pp.plot(data_array(ndim=2))


def test_plot_from_node():
    da = data_array(ndim=2)
    pp.plot(pp.Node(da))


def test_plot_data_array_2d_with_one_missing_coord_and_binedges():
    da = sc.data.table_xyz(100).bin(x=10, y=12).bins.mean()
    del da.coords['x']
    pp.plot(da)


def test_plot_2d_coord():
    da = data_array(ndim=2, ragged=True)
    pp.plot(da)
    pp.plot(da.transpose())


def test_plot_2d_coord_with_mask():
    da = data_array(ndim=2, ragged=True)
    da.masks['negative'] = da.data < sc.scalar(0, unit='m/s')
    pp.plot(da)


def test_kwarg_cmap():
    da = data_array(ndim=2)
    p = pp.plot(da, cmap='magma')
    assert p._view.colormapper.cmap.name == 'magma'


def test_kwarg_scale_2d():
    da = data_array(ndim=2)
    p = pp.plot(da, scale={'xx': 'log', 'yy': 'log'})
    assert p.canvas.ax.get_xscale() == 'log'
    assert p.canvas.ax.get_yscale() == 'log'


def test_raises_ValueError_when_given_binned_data():
    da = sc.data.table_xyz(100).bin(x=10, y=20)
    with pytest.raises(ValueError, match='Cannot plot binned data'):
        pp.plot(da)


def test_use_non_dimension_coords():
    da = data_array(ndim=2, binedges=True)
    da.coords['xx2'] = 7.5 * da.coords['xx']
    da.coords['yy2'] = 3.3 * da.coords['yy']
    p = pp.plot(da, coords=['xx2', 'yy2'])
    assert p.canvas.dims['x'] == 'xx2'
    assert p.canvas.dims['y'] == 'yy2'
    assert p.canvas.xmax == 7.5 * da.coords['xx'].max().value
    assert p.canvas.ymax == 3.3 * da.coords['yy'].max().value


@pytest.mark.parametrize('ext', ['jpg', 'png', 'pdf', 'svg'])
def test_save_to_disk_2d(ext):
    da = data_array(ndim=2)
    fig = pp.plot(da)
    with tempfile.TemporaryDirectory() as path:
        fname = os.path.join(path, f'plopp_fig2d.{ext}')
        fig.save(filename=fname)
        assert os.path.isfile(fname)


def test_save_to_disk_with_bad_extension_raises():
    da = data_array(ndim=2)
    fig = pp.plot(da)
    with pytest.raises(ValueError):
        fig.save(filename='plopp_fig2d.txt')


def test_plot_raises_with_multiple_2d_inputs():
    a = data_array(ndim=2)
    b = 3.3 * a
    with pytest.raises(
        ValueError, match='The plot function can only plot a single 2d data entry'
    ):
        pp.plot({'a': a, 'b': b})


def test_plot_xarray_data_array_2d():
    import xarray as xr

    N = 50
    M = 40
    data = np.random.random([M, N])
    time = np.arange(float(N))
    space = np.arange(float(M))
    da = xr.DataArray(
        data, coords={'space': space, 'time': time}, dims=['space', 'time']
    )
    p = pp.plot(da)
    assert p.canvas.dims['x'] == 'time'
    assert p.canvas.dims['y'] == 'space'
    assert p.canvas.units['x'] == 'dimensionless'
    assert p.canvas.units['y'] == 'dimensionless'


def test_plot_2d_ignores_masked_data_for_colorbar_range():
    da = data_array(ndim=2)
    da['xx', 10]['yy', 10].values = 100
    da.masks['m'] = da.data > sc.scalar(5.0, unit='m/s')
    p = pp.plot(da)
    assert p._view.colormapper.vmax < 100


def test_plot_2d_includes_masked_data_in_horizontal_range():
    da = data_array(ndim=2)
    da.masks['left'] = da.coords['xx'] < sc.scalar(5.0, unit='m')
    da.masks['right'] = da.coords['xx'] > sc.scalar(30.0, unit='m')
    p = pp.plot(da)
    assert p.canvas.xmin < 1.0
    assert p.canvas.xmax > 40.0


def test_plot_2d_includes_masked_data_in_vertical_range():
    da = data_array(ndim=2)
    da.masks['bottom'] = da.coords['yy'] < sc.scalar(5.0, unit='m')
    da.masks['top'] = da.coords['yy'] > sc.scalar(20.0, unit='m')
    p = pp.plot(da)
    assert p.canvas.ymin < 1.0
    assert p.canvas.ymax > 30.0


def test_plot_2d_datetime_coord():
    t = np.arange(
        np.datetime64('2017-03-16T20:58:17'), np.datetime64('2017-03-16T21:15:17'), 20
    )
    time = sc.array(dims=['time'], values=t)
    z = sc.arange('z', 50.0, unit='m')
    v = np.random.random(z.shape + time.shape)
    da = sc.DataArray(
        data=sc.array(dims=['z', 'time'], values=10 * v, variances=v),
        coords={'time': time, 'z': z},
    )
    pp.plot(da)


def test_plot_2d_datetime_coord_binedges():
    t = np.arange(
        np.datetime64('2017-03-16T20:58:17'), np.datetime64('2017-03-16T21:15:17'), 20
    )
    time = sc.array(dims=['time'], values=t)
    z = sc.arange('z', 50.0, unit='m')
    v = np.random.random(z[:-1].shape + time[:-1].shape)
    da = sc.DataArray(
        data=sc.array(dims=['z', 'time'], values=10 * v, variances=v),
        coords={'time': time, 'z': z},
    )
    pp.plot(da)
