# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.core.utils import coord_as_bin_edges, make_compatible
import scipp as sc
import pytest


def test_coord_as_bin_edges_midpoints_input():
    da = sc.DataArray(data=sc.arange('x', 5., unit='K'),
                      coords={'x': sc.arange('x', 5., unit='m')})
    result = coord_as_bin_edges(da, key='x')
    assert sc.identical(result, sc.linspace('x', -0.5, 4.5, num=6, unit='m'))


def test_coord_as_bin_edges_edges_input():
    x = sc.arange('x', 6., unit='m')
    da = sc.DataArray(data=sc.arange('x', 5., unit='K'), coords={'x': x})
    result = coord_as_bin_edges(da, key='x')
    assert sc.identical(result, x)


def test_coord_as_bin_edges_string_midpoints_input():
    strings = ['a', 'b', 'c', 'd', 'e']
    da = sc.DataArray(data=sc.arange('x', 5., unit='K'),
                      coords={'x': sc.array(dims=['x'], values=strings, unit='s')})
    result = coord_as_bin_edges(da, key='x')
    assert sc.identical(result, sc.linspace('x', -0.5, 4.5, num=6, unit='s'))


def test_coord_as_bin_edges_string_edges_input():
    strings = ['a', 'b', 'c', 'd', 'e', 'f']
    da = sc.DataArray(data=sc.arange('x', 5., unit='K'),
                      coords={'x': sc.array(dims=['x'], values=strings, unit='s')})
    result = coord_as_bin_edges(da, key='x')
    assert sc.identical(result, sc.arange('x', 6.0, unit='s'))


def test_coord_as_bin_edges_int_midpoints_input():
    da = sc.DataArray(data=sc.arange('x', 5., unit='K'),
                      coords={'x': sc.arange('x', 5, unit='m')})
    result = coord_as_bin_edges(da, key='x')
    assert sc.identical(result, sc.linspace('x', -0.5, 4.5, num=6, unit='m'))


def test_coord_as_bin_edges_int_edges_input():
    x = sc.arange('x', 6, unit='m')
    da = sc.DataArray(data=sc.arange('x', 5., unit='K'), coords={'x': x})
    result = coord_as_bin_edges(da, key='x')
    assert sc.identical(result, x)


def test_coord_as_bin_edges_non_dimension_coord():
    da = sc.DataArray(data=sc.arange('x', 5., unit='K'),
                      coords={
                          'x': sc.arange('x', 5., unit='m'),
                          'y': sc.arange('x', 17., 22., unit='m')
                      })
    result = coord_as_bin_edges(da, key='y', dim='x')
    assert sc.identical(result, sc.linspace('x', 16.5, 21.5, num=6, unit='m'))


def test_make_compatible_raises_different_dimension():
    x = sc.arange('x', 6., unit='m')
    with pytest.raises(sc.DimensionError):
        make_compatible(x, dim='y', unit='m')


def test_make_compatible_raises_incompatible_unit():
    x = sc.arange('x', 6., unit='m')
    with pytest.raises(sc.UnitError):
        make_compatible(x, unit='s')


def test_make_compatible_comverts_compatible_unit():
    x = sc.array(dims=['x'], values=[1., 4., 9.], unit='s')
    expected = sc.array(dims=['x'], values=[1000., 4000., 9000.], unit='ms')
    result = make_compatible(x, unit='ms')
    assert sc.identical(result, expected)


def test_make_compatible_comverts_compatible_unit_integers():
    x = sc.array(dims=['x'], values=[10, 20, 30, 40, 50], unit='cm')
    expected = sc.array(dims=['x'], values=[0.1, 0.2, 0.3, 0.4, 0.5], unit='m')
    result = make_compatible(x, unit='m')
    assert sc.identical(result, expected)
