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


def test_scatter_two_inputs():
    a = scatter_data()
    b = scatter_data(seed=2) * 10.0
    b.coords['x'] += sc.scalar(50.0, unit='m')
    pp.scatter({'a': a, 'b': b})


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
    with pytest.raises(ValueError, match="Use 'size' instead of 's' for scatter plot."):
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
        fig.update(new=data_array(ndim=2, dim_list="xyzab"))
    with pytest.raises(
        sc.DimensionError, match='Scatter only accepts data with 1 dimension'
    ):
        fig.update(new=data_array(ndim=3, dim_list="xyzab"))
