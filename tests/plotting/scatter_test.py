# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

import pytest
import scipp as sc

import plopp as pp
from plopp.data.testing import data_array
from plopp.data.testing import scatter as scatter_data

pytestmark = pytest.mark.usefixtures("_parametrize_mpl_backends")


def test_scatter_simple():
    pp.scatter(scatter_data())


def test_scatter_styling():
    pp.scatter(scatter_data(), color='r', marker='P')


def test_scatter_other_coords():
    a = scatter_data()
    a.coords['x2'] = a.coords['x'] ** 2
    pp.scatter(a, x='x2', y='z')


def test_scatter_pos():
    a = scatter_data()
    pp.scatter(a, pos='position')


def test_scatter_two_inputs():
    a = scatter_data()
    b = scatter_data(seed=2) * 10.0
    b.coords['x'] += sc.scalar(50.0, unit='m')
    pp.scatter({'a': a, 'b': b})


def test_scatter_multi_input_ylabel_drops_name():
    a = pp.data.scatter()
    b = pp.data.scatter(seed=2) * 10.0
    b.coords['x'] += sc.scalar(50.0, unit='m')

    fig = pp.scatter({'a': a, 'b': b})
    assert fig.canvas.ylabel == '[K]'


def test_scatter_multi_input_non_xy_dims_ylabel_drops_name():
    a = sc.DataArray(
        data=sc.linspace('point', 0.0, 4.0, 5, unit='K'),
        coords={
            'u': sc.linspace('point', 0.0, 4.0, 5, unit='m'),
            'v': sc.linspace('point', -2.0, 2.0, 5, unit='m'),
        },
    )
    b = sc.DataArray(
        data=sc.linspace('point', 1.0, 5.0, 5, unit='K'),
        coords={
            'u': sc.linspace('point', 10.0, 14.0, 5, unit='m'),
            'v': sc.linspace('point', -2.0, 2.0, 5, unit='m'),
        },
    )

    fig = pp.scatter({'a': a, 'b': b}, x='u', y='v')
    assert fig.canvas.ylabel == '[K]'


def test_scatter_two_inputs_color():
    a = scatter_data()
    b = scatter_data(seed=2) * 10.0
    b.coords['x'] += sc.scalar(50.0, unit='m')
    pp.scatter({'a': a, 'b': b}, color={'a': 'k', 'b': 'g'})


def test_scatter_with_colorbar():
    scat = pp.scatter(scatter_data(), cbar=True)
    assert scat.view.colormapper is not None


def test_scatter_with_cmap():
    name = 'magma'
    scat = pp.scatter(scatter_data(), cbar=True, cmap=name)
    assert scat.view.colormapper.cmap.name == name


def test_scatter_with_int_size():
    a = scatter_data()
    pp.scatter(a, size=10)


def test_scatter_with_float_size():
    a = scatter_data()
    pp.scatter(a, size=33.3)


def test_scatter_with_variable_size():
    a = scatter_data()
    a.coords['s'] = sc.abs(a.coords['x']) * 5
    pp.scatter(a, size='s')


def test_scatter_with_size_and_cbar():
    a = scatter_data()
    a.coords['s'] = sc.abs(a.coords['x']) * 5
    pp.scatter(a, size='s', cbar=True)


def test_scatter_with_s_kwarg_raises():
    a = scatter_data()
    with pytest.raises(ValueError, match="Use 'size' instead of 's' for scatter plot"):
        pp.scatter(a, s=10)


def test_scatter_with_masks():
    a = scatter_data()
    a.masks['m'] = a.coords['x'] > sc.scalar(10, unit='m')
    pp.scatter(a)


def test_scatter_flattens_2d_data():
    pp.scatter(data_array(ndim=2), x='xx', y='yy', cbar=True)


def test_scatter_with_norm():
    a = scatter_data()
    scat = pp.scatter(a, cbar=True, norm='linear')
    assert scat.view.colormapper.norm == 'linear'
    scat = pp.scatter(a, cbar=True, norm='log')
    assert scat.view.colormapper.norm == 'log'


def test_scatter_log_axes():
    a = scatter_data()
    scat = pp.scatter(a)
    assert scat.view.canvas.xscale == 'linear'
    assert scat.view.canvas.yscale == 'linear'
    scat = pp.scatter(a, scale={'x': 'log', 'y': 'log'})
    assert scat.view.canvas.xscale == 'log'
    assert scat.view.canvas.yscale == 'log'


def test_scatter_does_not_accept_data_with_other_dimensionality_on_update():
    da = scatter_data()
    fig = pp.scatter(da)
    with pytest.raises(
        sc.DimensionError, match='Scatter only accepts data with 1 dimension'
    ):
        fig.update(new=da.fold(dim=da.dim, sizes={'a': 2, 'b': -1}))
    with pytest.raises(
        sc.DimensionError, match='Scatter only accepts data with 1 dimension'
    ):
        fig.update(new=da.fold(dim=da.dim, sizes={'a': 2, 'b': 2, 'c': -1}))


def test_xmin():
    da = scatter_data()
    fig = pp.scatter(da, xmin=sc.scalar(2.5, unit='m'))
    assert fig.canvas.xmin == 2.5


def test_xmin_no_unit():
    da = scatter_data()
    fig = pp.scatter(da, xmin=2.5)
    assert fig.canvas.xmin == 2.5


def test_xmax():
    da = scatter_data()
    fig = pp.scatter(da, xmax=sc.scalar(7.5, unit='m'))
    assert fig.canvas.xmax == 7.5


def test_xmax_no_unit():
    da = scatter_data()
    fig = pp.scatter(da, xmax=8.1)
    assert fig.canvas.xmax == 8.1


def test_ymin():
    da = scatter_data()
    fig = pp.scatter(da, ymin=sc.scalar(-0.5, unit='m'))
    assert fig.canvas.ymin == -0.5


def test_ymin_no_unit():
    da = scatter_data()
    fig = pp.scatter(da, ymin=-0.6)
    assert fig.canvas.ymin == -0.6


def test_ymax():
    da = scatter_data()
    fig = pp.scatter(da, ymax=sc.scalar(0.68, unit='m'))
    assert fig.canvas.ymax == 0.68


def test_ymax_no_unit():
    da = scatter_data()
    fig = pp.scatter(da, ymax=5.69)
    assert fig.canvas.ymax == 5.69


def test_cmin():
    da = scatter_data()
    fig = pp.scatter(da, cbar=True, cmin=sc.scalar(2.5, unit='K'))
    assert fig.view.colormapper.cmin == 2.5


def test_cmin_no_unit():
    da = scatter_data()
    fig = pp.scatter(da, cbar=True, cmin=3.3)
    assert fig.view.colormapper.cmin == 3.3


def test_cmax():
    da = scatter_data()
    fig = pp.scatter(da, cbar=True, cmax=sc.scalar(7.5, unit='K'))
    assert fig.view.colormapper.cmax == 7.5


def test_cmax_no_unit():
    da = scatter_data()
    fig = pp.scatter(da, cbar=True, cmax=8.1)
    assert fig.view.colormapper.cmax == 8.1


def test_logx():
    da = scatter_data()
    fig = pp.scatter(da, logx=True)
    assert fig.canvas.xscale == 'log'
    assert fig.canvas.yscale == 'linear'


def test_logy():
    da = scatter_data()
    fig = pp.scatter(da, logy=True)
    assert fig.canvas.yscale == 'log'
    assert fig.canvas.xscale == 'linear'


def test_logc():
    da = scatter_data()
    fig = pp.scatter(da, cbar=True, logc=True)
    assert fig.view.colormapper.norm == 'log'


def test_xlabel():
    da = scatter_data()
    fig = pp.scatter(da, xlabel='MyXLabel')
    assert fig.canvas.xlabel == 'MyXLabel'


def test_ylabel():
    da = scatter_data()
    fig = pp.scatter(da, ylabel='MyYLabel')
    assert fig.canvas.ylabel == 'MyYLabel'


def test_clabel():
    da = scatter_data()
    fig = pp.scatter(da, cbar=True, clabel='MyColorLabel')
    assert fig.view.colormapper.clabel == 'MyColorLabel'
