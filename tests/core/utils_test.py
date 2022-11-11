# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.core.utils import coord_as_bin_edges
import scipp as sc


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
