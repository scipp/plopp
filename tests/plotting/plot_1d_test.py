# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import os
import tempfile

import numpy as np
import pytest
import scipp as sc

import plopp as pp
from plopp.data.testing import data_array, dataset

pytestmark = pytest.mark.usefixtures("_parametrize_all_backends")


def _skip_if_kaleido_not_installed():
    if pp.backends['2d'] == 'plotly':
        try:
            import kaleido as kldo
        except ImportError:
            kldo = None
        if kldo is None:
            pytest.skip("Skipping because kaleido is not installed")


def test_plot_ndarray():
    pp.plot(np.arange(50.0))


def test_plot_ndarray_int():
    pp.plot(np.arange(50))


def test_plot_list():
    pp.plot([1.0, 2.0, 3.0, 4.0, 5.0])


def test_plot_list_int():
    pp.plot([1, 2, 3, 4, 5])


def test_plot_variable():
    pp.plot(sc.arange('x', 50.0))


def test_plot_data_array():
    pp.plot(data_array(ndim=1))


def test_plot_data_array_missing_coords():
    da = sc.data.table_xyz(100)
    pp.plot(da)
    assert 'row' not in da.coords


def test_plot_dataset():
    ds = dataset(ndim=1)
    pp.plot(ds)


def test_plot_dict_of_ndarrays():
    pp.plot({'a': np.arange(50.0), 'b': np.arange(60.0)})


def test_plot_dict_of_lists():
    pp.plot({'a': [1, 2, 3, 4], 'b': [4, 5, 6, 7]})


def test_plot_dict_of_variables():
    pp.plot({'a': sc.arange('x', 50.0), 'b': sc.arange('x', 60.0)})


def test_plot_dict_of_data_arrays():
    ds = dataset(ndim=1)
    pp.plot({'a': ds['a'], 'b': ds['b']})


def test_plot_from_node():
    da = data_array(ndim=1)
    pp.plot(pp.Node(da))


def test_plot_multiple_inputs_raises():
    da = data_array(ndim=1)
    with pytest.raises(TypeError, match='takes 1 positional argument'):
        pp.plot(da, 3.3 * da)


def test_plot_dict_of_nodes():
    a = data_array(ndim=1)
    b = 6.7 * a
    pp.plot({'a': pp.Node(a), 'b': pp.Node(b)})


def test_plot_mixing_raw_data_and_nodes():
    a = data_array(ndim=1)
    b = 13.3 * a
    pp.plot({'a': a, 'b': pp.Node(b)})
    pp.plot({'a': pp.Node(a), 'b': b})


def test_plot_coord_with_no_unit():
    da = sc.data.table_xyz(100).bin(x=10).bins.mean()
    da.coords['x'].unit = None
    pp.plot(da)


def test_plot_rejects_large_input():
    error_match = "may take very long or use an excessive amount of memory"
    with pytest.raises(ValueError, match=error_match):
        pp.plot(np.random.random(1_100_000))
    with pytest.raises(ValueError, match=error_match):
        pp.plot(np.random.random((3000, 2500)))


def test_plot_ignore_size_disables_size_check():
    pp.plot(np.random.random(1_100_000), ignore_size=True)


def test_plot_with_non_dimensional_unsorted_coord_does_not_warn():
    da = data_array(ndim=1)
    da.coords['aux'] = sc.sin(sc.arange(da.dim, 50.0, unit='rad'))
    pp.plot(da)


def test_linecolor():
    da = data_array(ndim=1)
    fig = pp.plot(da, color='red')
    [line] = fig.view.artists.values()
    assert line.color == 'red'


def test_norm():
    da = data_array(ndim=1)
    p = pp.plot(da, norm='log')
    assert p.canvas.yscale == 'log'


def test_scale():
    da = data_array(ndim=1)
    p = pp.plot(da, scale={'xx': 'log'})
    assert p.canvas.xscale == 'log'
    assert p.canvas.yscale == 'linear'


def test_kwarg_for_two_lines():
    a = data_array(ndim=1)
    b = 2.0 * a
    fig = pp.plot({'a': a, 'b': b}, color='red')
    [line_a, line_b] = fig.view.artists.values()
    assert line_a.color == 'red'
    assert line_b.color == 'red'


def test_kwarg_as_dict():
    a = data_array(ndim=1)
    b = 2.0 * a
    fig = pp.plot({'a': a, 'b': b}, color={'a': 'red', 'b': 'black'})
    [line_a, line_b] = fig.view.artists.values()
    assert line_a.color == 'red'
    assert line_b.color == 'black'


def test_raises_ValueError_when_given_binned_data():
    da = sc.data.table_xyz(100).bin(x=10)
    with pytest.raises(ValueError, match='Cannot plot binned data'):
        pp.plot(da)


def test_raises_ValueError_when_given_unsupported_data_type():
    a = data_array(ndim=1)
    b = a * 2.0
    c = a * 3.0
    d = a * 4.0
    nested_dict = {'group1': {'a': a, 'b': b}, 'group2': {'c': c, 'd': d}}
    with pytest.raises(TypeError, match='Cannot convert input of type'):
        pp.plot(nested_dict)


def test_use_non_dimension_coords_dataset():
    ds = dataset(ndim=1)
    ds.coords['xx2'] = 6.6 * ds.coords['xx']
    p = pp.plot(ds, coords=['xx2'])
    assert p.canvas.dims['x'] == 'xx2'
    assert p.canvas.xmax > 6.6 * ds.coords['xx'].max().value


@pytest.mark.parametrize('ext', ['jpg', 'png', 'pdf', 'svg'])
def test_save_to_disk_1d(ext):
    _skip_if_kaleido_not_installed()
    da = data_array(ndim=1)
    fig = pp.plot(da)
    with tempfile.TemporaryDirectory() as path:
        fname = os.path.join(path, f'plopp_fig1d.{ext}')
        fig.save(filename=fname)
        assert os.path.isfile(fname)


def test_save_to_disk_with_bad_extension_raises():
    _skip_if_kaleido_not_installed()
    da = data_array(ndim=1)
    fig = pp.plot(da)
    with pytest.raises(ValueError, match='txt'):
        fig.save(filename='plopp_fig1d.txt')


def test_plot_xarray_data_array_1d():
    import xarray as xr

    N = 50
    data = np.random.random(N)
    time = np.arange(float(N))
    da = xr.DataArray(data, coords={'time': time}, dims=['time'])
    p = pp.plot(da)
    assert p.canvas.dims['x'] == 'time'
    assert p.canvas.units['x'] == 'dimensionless'
    assert p.canvas.units['data'] == 'dimensionless'


def test_plot_xarray_dataset():
    import xarray as xr

    N = 50
    temp = 15 + 8 * np.random.random(N)
    precip = 10 * np.random.random(N)
    ds = xr.Dataset(
        {
            "temperature": (["time"], temp),
            "precipitation": (["time"], precip),
        },
        coords={"time": np.arange(50)},
    )
    p = pp.plot(ds)
    assert p.canvas.dims['x'] == 'time'
    assert p.canvas.units['x'] == 'dimensionless'
    assert p.canvas.units['data'] == 'dimensionless'
    assert len(p.view.artists) == 2


def test_plot_pandas_series():
    import pandas as pd

    s = pd.Series(np.arange(100.0), name='MyDataSeries')
    p = pp.plot(s)
    assert p.canvas.dims['x'] == 'row'
    [line] = p.view.artists.values()
    assert line.label == 'MyDataSeries'


def test_plot_pandas_dataframe():
    import pandas as pd

    df = pd.DataFrame(
        {
            'A': np.arange(50.0),
            'B': 1.5 * np.arange(50),
            'C': np.random.random(50),
            'D': np.random.normal(size=50),
        }
    )
    p = pp.plot(df)
    assert p.canvas.dims['x'] == 'row'
    assert len(p.view.artists) == 4


@pytest.mark.parametrize('Constructor', [dict, sc.Dataset, sc.DataGroup])
def test_names_are_overridden_when_plotting_dicts(Constructor):
    da1 = data_array(ndim=1)
    da2 = da1 * 2
    da1.name = "DA1"
    da2.name = "DA2"
    p = pp.plot(Constructor({'a': da1, 'b': da2}))
    artists = list(p.view.artists.values())
    assert artists[0].label == 'a'
    assert artists[1].label == 'b'
    assert da1.name == 'DA1'
    assert da2.name == 'DA2'


def test_plot_1d_ignores_masked_data_for_vertical_range():
    da = data_array(ndim=1)
    da.values[10] = 100
    da.masks['m'] = da.data > sc.scalar(5.0, unit='m/s')
    p = pp.plot(da)
    assert p.canvas.ymax < 100


def test_plot_1d_includes_masked_data_in_horizontal_range():
    da = data_array(ndim=1)
    da.masks['m'] = da.coords['xx'] > sc.scalar(5.0, unit='m')
    p = pp.plot(da)
    # If we check only for > 5, padding may invalidate the test
    assert p.canvas.xmax > 10.0


def test_plot_1d_datetime_coord():
    t = np.arange(
        np.datetime64('2017-03-16T20:58:17'), np.datetime64('2017-03-16T21:15:17'), 20
    )
    time = sc.array(dims=['time'], values=t)
    v = np.random.rand(time.sizes['time'])
    da = sc.DataArray(
        data=sc.array(dims=['time'], values=10 * v, variances=v),
        coords={'time': time},
    )
    pp.plot(da)


def test_plot_1d_datetime_coord_binedges():
    t = np.arange(
        np.datetime64('2017-03-16T20:58:17'), np.datetime64('2017-03-16T21:15:17'), 20
    )
    time = sc.array(dims=['time'], values=t)
    v = np.random.rand(time.sizes['time'] - 1)
    da = sc.DataArray(
        data=sc.array(dims=['time'], values=10 * v, variances=v),
        coords={'time': time},
    )
    pp.plot(da)


def test_plot_1d_datetime_coord_with_mask():
    t = np.arange(
        np.datetime64('2017-03-16T20:58:17'), np.datetime64('2017-03-16T21:15:17'), 20
    )
    time = sc.array(dims=['time'], values=t)
    v = np.random.rand(time.sizes['time'])
    da = sc.DataArray(
        data=sc.array(dims=['time'], values=10 * v, variances=v),
        coords={'time': time},
        masks={'m': time > sc.datetime('2017-03-16T21:10:00')},
    )
    pp.plot(da)


def test_plot_1d_datetime_coord_with_mask_and_binedges():
    t = np.arange(
        np.datetime64('2017-03-16T20:58:17'), np.datetime64('2017-03-16T21:15:17'), 20
    )
    time = sc.array(dims=['time'], values=t)
    v = np.random.rand(time.sizes['time'] - 1)
    da = sc.DataArray(
        data=sc.array(dims=['time'], values=10 * v, variances=v),
        coords={'time': time},
        masks={'m': sc.midpoints(time) > sc.datetime('2017-03-16T21:10:00')},
    )
    pp.plot(da)


def test_plot_1d_datetime_coord_log():
    if pp.backends['2d'] == 'plotly':
        pytest.skip('Log scale with datetime not supported in plotly')
    t = np.arange(
        np.datetime64('2017-03-16T20:58:17'), np.datetime64('2017-03-16T21:15:17'), 20
    )
    time = sc.array(dims=['time'], values=t)
    v = np.random.rand(time.sizes['time'])
    da = sc.DataArray(
        data=sc.array(dims=['time'], values=10 * v, variances=v),
        coords={'time': time},
    )
    pp.plot(da, scale={'time': 'log'})


def test_plot_1d_datetime_coord_log_binedges():
    if pp.backends['2d'] == 'plotly':
        pytest.skip('Log scale with datetime not supported in plotly')
    t = np.arange(
        np.datetime64('2017-03-16T20:58:17'), np.datetime64('2017-03-16T21:15:17'), 20
    )
    time = sc.array(dims=['time'], values=t)
    v = np.random.rand(time.sizes['time'] - 1)
    da = sc.DataArray(
        data=sc.array(dims=['time'], values=10 * v, variances=v),
        coords={'time': time},
    )
    pp.plot(da, scale={'time': 'log'})


def test_plot_1d_datetime_coord_log_with_mask():
    if pp.backends['2d'] == 'plotly':
        pytest.skip('Log scale with datetime not supported in plotly')
    t = np.arange(
        np.datetime64('2017-03-16T20:58:17'), np.datetime64('2017-03-16T21:15:17'), 20
    )
    time = sc.array(dims=['time'], values=t)
    v = np.random.rand(time.sizes['time'])
    da = sc.DataArray(
        data=sc.array(dims=['time'], values=10 * v, variances=v),
        coords={'time': time},
        masks={'m': time > sc.datetime('2017-03-16T21:10:00')},
    )
    pp.plot(da, scale={'time': 'log'})


def test_plot_1d_datetime_data():
    t = np.arange(
        np.datetime64('2017-03-16T20:58:17'), np.datetime64('2017-03-16T21:15:17'), 20
    )
    time = sc.array(dims=['time'], values=t)
    da = sc.DataArray(
        data=time,
        coords={'x': sc.arange('time', len(time), unit='m')},
    )
    pp.plot(da)


def test_plot_1d_datetime_length_1():
    da = sc.DataArray(
        sc.array(dims=['time'], values=[3], unit='deg'),
        coords={'time': sc.datetimes(dims=['time'], values=['now'], unit='s')},
    )
    pp.plot(da)


def test_plot_1d_extra_datetime_coord_binedges():
    da = data_array(ndim=1)
    dim = da.dim
    size = da.sizes[dim]
    da.coords['times'] = (sc.arange('t', 2 * size, unit='s') + sc.epoch(unit='s')).fold(
        dim='t', sizes={dim: size, 't': 2}
    )
    pp.plot(da)


def test_plot_1d_data_with_errorbars():
    da = data_array(ndim=1, variances=True)
    p = da.plot()
    assert p.canvas.ymin < -1.0
    assert p.canvas.ymax > 1.0


def test_plot_1d_data_with_variances_and_nan_values():
    da = data_array(ndim=1, variances=True)
    da.values[-10:] = np.nan
    p = da.plot()
    assert p.canvas.ymin < -1.0
    assert p.canvas.ymax > 1.0


def test_plot_1d_data_with_binedges():
    da = data_array(ndim=1, binedges=True)
    da.plot()


def test_autoscale_after_update_grows_limits():
    da = data_array(ndim=1)
    fig = da.plot()
    old_lims = fig.canvas.yrange
    [key] = fig.artists.keys()
    fig.update({key: da * 2.5})
    fig.view.autoscale()
    new_lims = fig.canvas.yrange
    assert new_lims[0] < old_lims[0]
    assert new_lims[1] > old_lims[1]


def test_autoscale_after_update_shrinks_limits():
    da = data_array(ndim=1)
    fig = da.plot()
    old_lims = fig.canvas.yrange
    [key] = fig.artists.keys()
    const = 0.5
    fig.update({key: da * const})
    fig.view.autoscale()
    new_lims = fig.canvas.yrange
    assert new_lims[0] == old_lims[0] * const
    assert new_lims[1] == old_lims[1] * const


def test_vmin():
    da = data_array(ndim=1)
    fig = da.plot(vmin=sc.scalar(-0.5, unit='m/s'))
    assert fig.canvas.ymin == -0.5


def test_vmin_unit_mismatch_raises():
    da = data_array(ndim=1)
    with pytest.raises(sc.UnitError):
        _ = da.plot(vmin=sc.scalar(-0.5, unit='m'))


def test_vmax():
    da = data_array(ndim=1)
    fig = da.plot(vmax=sc.scalar(0.68, unit='m/s'))
    assert fig.canvas.ymax == 0.68


def test_vmin_vmax():
    da = data_array(ndim=1)
    fig = da.plot(
        vmin=sc.scalar(-0.5, unit='m/s'),
        vmax=sc.scalar(0.68, unit='m/s'),
    )
    assert np.allclose(fig.canvas.yrange, [-0.5, 0.68])


def test_autoscale_after_update_does_not_change_limits_if_vmin_vmax():
    da = data_array(ndim=1)
    fig = da.plot(vmin=-0.51, vmax=0.78)
    assert np.allclose(fig.canvas.yrange, [-0.51, 0.78])
    old_lims = fig.canvas.yrange
    [key] = fig.artists.keys()
    fig.update({key: da * 2.5})
    fig.view.autoscale()
    assert np.allclose(fig.canvas.yrange, old_lims)


def test_vmin_vmax_no_variable():
    da = data_array(ndim=1)
    fig = da.plot(vmin=-0.5, vmax=0.68)
    assert np.allclose(fig.canvas.yrange, [-0.5, 0.68])


def test_1d_plot_does_not_accept_higher_dimension_data_on_update():
    da = data_array(ndim=1)
    fig = da.plot()
    with pytest.raises(
        sc.DimensionError, match='Line only accepts data with 1 dimension'
    ):
        fig.update(new=data_array(ndim=2))
    with pytest.raises(
        sc.DimensionError, match='Line only accepts data with 1 dimension'
    ):
        fig.update(new=data_array(ndim=3))


def test_figure_has_data_name_on_vertical_axis_for_one_curve():
    da = data_array(ndim=1)
    da.name = "Velocity"
    fig = da.plot()
    ylabel = fig.canvas.ylabel
    assert da.name in ylabel
    assert str(da.unit) in ylabel


def test_figure_has_data_name_on_vertical_axis_for_dict_with_one_entry():
    da = data_array(ndim=1)
    fig = pp.plot({"Velocity": da})
    ylabel = fig.canvas.ylabel
    assert da.name in ylabel
    assert str(da.unit) in ylabel


def test_figure_has_only_unit_on_vertical_axis_for_multiple_curves():
    a = data_array(ndim=1)
    a.name = "Velocity"
    b = a * 1.67
    b.name = "Speed"

    fig = pp.plot({'a': a, 'b': b})
    ylabel = fig.canvas.ylabel
    assert str(a.unit) in ylabel
    assert str(b.unit) in ylabel
    assert a.name not in ylabel
    assert b.name not in ylabel

    c = a * 2.5
    c.name = "Rate"
    fig = pp.plot({'a': a, 'b': b, 'c': c})
    ylabel = fig.canvas.ylabel
    assert str(a.unit) in ylabel
    assert a.name not in ylabel
    assert b.name not in ylabel
    assert c.name not in ylabel


def test_plot_1d_scalar_mask():
    da = sc.DataArray(
        sc.ones(sizes={'x': 3}),
        coords={'x': sc.arange('x', 3)},
        masks={'m': sc.scalar(False)},
    )
    _ = da.plot()


def test_plot_1d_all_values_masked():
    da = data_array(ndim=1)
    da.masks['m'] = sc.scalar(True)
    _ = da.plot()


def test_plot_1d_all_values_masked_with_errorbars():
    da = data_array(ndim=1, variances=True)
    da.masks['m'] = sc.scalar(True)
    _ = da.plot()
