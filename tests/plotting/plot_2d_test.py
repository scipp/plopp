# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import os
import tempfile

import numpy as np
import pytest
import scipp as sc

import plopp as pp
from plopp.data.testing import data_array, variable

pytestmark = pytest.mark.usefixtures("_parametrize_mpl_backends")


def test_plot_ndarray():
    pp.plot(np.arange(50.0).reshape(5, 10))


def test_plot_ndarray_int():
    pp.plot(np.arange(50).reshape(5, 10))


def test_plot_variable():
    pp.plot(variable(ndim=2))


@pytest.mark.parametrize('linspace', [True, False])
def test_plot_data_array(linspace):
    pp.plot(data_array(ndim=2, linspace=linspace))


@pytest.mark.parametrize('linspace', [True, False])
def test_plot_from_node(linspace):
    da = data_array(ndim=2, linspace=linspace)
    pp.plot(pp.Node(da))


@pytest.mark.parametrize('linspace', [True, False])
def test_plot_data_array_2d_with_one_missing_coord_and_binedges(linspace):
    xbins = sc.linspace('x', 0, 1, 10, unit='m')
    if not linspace:
        xbins[-1] += sc.scalar(0.1, unit='m')
    da = sc.data.table_xyz(100).bin(x=xbins, y=12).bins.mean()
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


@pytest.mark.parametrize('linspace', [True, False])
def test_kwarg_norm(linspace):
    da = data_array(ndim=2, linspace=linspace)
    p = pp.plot(da, norm='log')
    assert p.view.colormapper.norm == 'log'


@pytest.mark.parametrize('linspace', [True, False])
def test_kwarg_cmap(linspace):
    da = data_array(ndim=2, linspace=linspace)
    p = pp.plot(da, cmap='magma')
    assert p.view.colormapper.cmap.name == 'magma'


@pytest.mark.parametrize('linspace', [True, False])
def test_kwarg_scale_2d(linspace):
    da = data_array(ndim=2, linspace=linspace)
    p = pp.plot(da, scale={'xx': 'log', 'yy': 'log'})
    assert p.canvas.ax.get_xscale() == 'log'
    assert p.canvas.ax.get_yscale() == 'log'


def test_raises_ValueError_when_given_binned_data():
    da = sc.data.table_xyz(100).bin(x=10, y=20)
    with pytest.raises(ValueError, match='Cannot plot binned data'):
        pp.plot(da)


@pytest.mark.parametrize('linspace', [True, False])
def test_use_non_dimension_coords(linspace):
    da = data_array(ndim=2, binedges=True, linspace=linspace)
    da.coords['xx2'] = 7.5 * da.coords['xx']
    da.coords['yy2'] = 3.3 * da.coords['yy']
    p = pp.plot(da, coords=['xx2', 'yy2'])
    assert p.canvas.dims['x'] == 'xx2'
    assert p.canvas.dims['y'] == 'yy2'
    assert p.canvas.xmax == 7.5 * da.coords['xx'].max().value
    assert p.canvas.ymax == 3.3 * da.coords['yy'].max().value


def test_use_two_coords_for_same_underlying_dimension_raises():
    da = data_array(ndim=2)
    da.coords['a'] = da.coords['xx'] * 2
    msg = "coords: Cannot use more than one coordinate"
    with pytest.raises(ValueError, match=msg):
        pp.plot(da, coords=['xx', 'a'])
    with pytest.raises(ValueError, match=msg):
        pp.plot(da, coords=['a', 'xx'])


@pytest.mark.parametrize('ext', ['jpg', 'png', 'pdf', 'svg'])
@pytest.mark.parametrize('linspace', [True, False])
def test_save_to_disk_2d(ext, linspace):
    da = data_array(ndim=2, linspace=linspace)
    fig = pp.plot(da)
    with tempfile.TemporaryDirectory() as path:
        fname = os.path.join(path, f'plopp_fig2d.{ext}')
        fig.save(filename=fname)
        assert os.path.isfile(fname)


@pytest.mark.parametrize('linspace', [True, False])
def test_save_to_disk_with_bad_extension_raises(linspace):
    da = data_array(ndim=2, linspace=linspace)
    fig = pp.plot(da)
    with pytest.raises(ValueError, match='txt'):
        fig.save(filename='plopp_fig2d.txt')


@pytest.mark.parametrize('linspace', [True, False])
def test_plot_raises_with_multiple_2d_inputs(linspace):
    a = data_array(ndim=2, linspace=linspace)
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


@pytest.mark.parametrize('linspace', [True, False])
def test_plot_2d_ignores_masked_data_for_colorbar_range(linspace):
    da = data_array(ndim=2, linspace=linspace)
    da['xx', 10]['yy', 10].values = 100
    da.masks['m'] = da.data > sc.scalar(5.0, unit='m/s')
    p = pp.plot(da)
    assert p.view.colormapper.vmax < 100


@pytest.mark.parametrize('linspace', [True, False])
def test_plot_2d_includes_masked_data_in_horizontal_range(linspace):
    da = data_array(ndim=2, linspace=linspace)
    da.masks['left'] = da.coords['xx'] < sc.scalar(5.0, unit='m')
    da.masks['right'] = da.coords['xx'] > sc.scalar(30.0, unit='m')
    p = pp.plot(da)
    assert p.canvas.xmin < 1.0
    assert p.canvas.xmax > 40.0


@pytest.mark.parametrize('linspace', [True, False])
def test_plot_2d_includes_masked_data_in_vertical_range(linspace):
    da = data_array(ndim=2, linspace=linspace)
    da.masks['bottom'] = da.coords['yy'] < sc.scalar(5.0, unit='m')
    da.masks['top'] = da.coords['yy'] > sc.scalar(20.0, unit='m')
    p = pp.plot(da)
    assert p.canvas.ymin < 1.0
    assert p.canvas.ymax > 30.0


@pytest.mark.parametrize('linspace', [True, False])
def test_plot_2d_datetime_coord(linspace):
    t = np.arange(
        np.datetime64('2017-03-16T20:58:17'), np.datetime64('2017-03-16T21:15:17'), 20
    )
    if not linspace:
        t[-1] += np.timedelta64(1, 's')
    time = sc.array(dims=['time'], values=t)
    z = sc.arange('z', 50.0, unit='m')
    v = np.random.random(z.shape + time.shape)
    da = sc.DataArray(
        data=sc.array(dims=['z', 'time'], values=10 * v, variances=v),
        coords={'time': time, 'z': z},
    )
    pp.plot(da)


@pytest.mark.parametrize('linspace', [True, False])
def test_plot_2d_datetime_coord_binedges(linspace):
    t = np.arange(
        np.datetime64('2017-03-16T20:58:17'), np.datetime64('2017-03-16T21:15:17'), 20
    )
    if not linspace:
        t[-1] += np.timedelta64(1, 's')
    time = sc.array(dims=['time'], values=t)
    z = sc.arange('z', 50.0, unit='m')
    v = np.random.random(z[:-1].shape + time[:-1].shape)
    da = sc.DataArray(
        data=sc.array(dims=['z', 'time'], values=10 * v, variances=v),
        coords={'time': time, 'z': z},
    )
    pp.plot(da)


@pytest.mark.parametrize('linspace', [True, False])
def test_create_with_bin_edges(linspace):
    da = data_array(ndim=2, binedges=True, linspace=linspace)
    fig = da.plot()
    assert len(fig.artists) == 1
    [img] = fig.artists.values()
    assert sc.identical(img._data, da)


@pytest.mark.parametrize('linspace', [True, False])
def test_create_with_only_one_bin_edge_coord(linspace):
    da = data_array(ndim=2, binedges=True, linspace=linspace)
    da.coords['xx'] = sc.midpoints(da.coords['xx'])
    fig = da.plot()
    assert len(fig.artists) == 1
    [img] = fig.artists.values()
    assert sc.identical(img._data, da)


def test_colorbar_label_has_correct_unit():
    da = data_array(ndim=2, unit='K')
    fig = da.plot()
    assert fig.canvas.cblabel == '[K]'


def test_colorbar_label_has_correct_name():
    da = data_array(ndim=2, unit='K')
    name = 'My Experimental Data'
    da.name = name
    fig = da.plot()
    assert fig.canvas.cblabel == name + ' [K]'


def test_axis_label_with_transposed_2d_coord():
    a = sc.linspace('a', 0, 1, 10, unit='m')
    b = sc.linspace('b', 0, 2, 5, unit='s')
    da = sc.DataArray(a * b, coords={'a': a, 'b': b * a})
    fig = da.plot()
    assert fig.canvas.xlabel == 'b [m*s]'
    da = sc.DataArray(a * b, coords={'a': a, 'b': a * b})
    fig2 = da.plot()
    assert fig2.canvas.xlabel == fig.canvas.xlabel


def test_plot_1d_data_over_2d_data():
    f = data_array(ndim=2).plot()
    data_array(ndim=1).plot(ax=f.ax)


def test_plot_1d_data_over_2d_data_datetime():
    # 2d data
    t = np.arange(
        np.datetime64('2017-03-16T20:58:17'), np.datetime64('2017-03-16T21:15:17'), 20
    )
    time = sc.array(dims=['time'], values=t)
    z = sc.arange('z', 50.0, unit='m')
    v = 10 * np.random.random(z.shape + time.shape)
    da2d = sc.DataArray(
        data=sc.array(dims=['z', 'time'], values=v), coords={'time': time, 'z': z}
    )
    fig2d = pp.plot(da2d)

    # 1d data
    v = np.random.rand(time.sizes['time'])
    da1d = sc.DataArray(data=sc.array(dims=['time'], values=v), coords={'time': time})
    pp.plot(da1d, ax=fig2d.ax)


@pytest.mark.parametrize('linspace', [True, False])
def test_no_cbar(linspace):
    da = data_array(ndim=2, linspace=linspace)
    fig = da.plot(cbar=True)
    assert fig.view.colormapper.colorbar is not None
    fig = da.plot(cbar=False)
    assert fig.view.colormapper.colorbar is None


def test_2d_plot_does_not_accept_data_with_other_dimensionality_on_update():
    da = data_array(ndim=2)
    fig = da.plot()
    # The data has no 'y' coordinate
    with pytest.raises(KeyError, match='Supplied data is incompatible with this view'):
        fig.update(new=data_array(ndim=1))
    # The data has 3 dimensions
    with pytest.raises(
        sc.DimensionError, match='Image only accepts data with 2 dimension'
    ):
        fig.update(new=data_array(ndim=3))


def test_figure_has_data_name_on_colorbar_for_one_image():
    da = data_array(ndim=2)
    da.name = "Velocity"
    fig = da.plot()
    ylabel = fig.view.colormapper.ylabel
    assert da.name in ylabel
    assert str(da.unit) in ylabel


@pytest.mark.parametrize('linspace', [True, False])
def test_figure_has_only_unit_on_colorbar_for_multiple_images(linspace):
    a = data_array(ndim=2, linspace=linspace)
    a.name = "Velocity"
    b = a * 1.67
    dim = b.dims[-1]
    b.coords[dim] += b.coords[dim].max() * 1.1
    b.name = "Speed"

    fig = pp.imagefigure(pp.Node(a), pp.Node(b), cbar=True)
    ylabel = fig.view.colormapper.ylabel
    assert str(a.unit) in ylabel
    assert str(b.unit) in ylabel
    assert a.name not in ylabel
    assert b.name not in ylabel


def test_plot_with_bin_edges_left_over_from_slicing():
    da = data_array(ndim=2, binedges=True)
    f = da.fold(dim='xx', sizes={'xx': 25, 'pulse': 2})
    f['pulse', 0].plot()


def test_plot_with_scalar_dimension_coord_raises():
    da = data_array(ndim=2)
    da.coords['xx'] = sc.scalar(333.0, unit='K')
    with pytest.raises(ValueError, match='Input data cannot be plotted'):
        da.plot()


def test_plot_2d_all_values_masked():
    da = data_array(ndim=2)
    da.masks['m'] = sc.scalar(True)
    _ = da.plot()
