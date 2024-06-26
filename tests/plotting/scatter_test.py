# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

import scipp as sc

import plopp as pp
from plopp.data.testing import data_array
from plopp.data.testing import scatter as scatter_data


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
    assert scat._view.colormapper is not None


def test_scatter_with_cmap():
    name = 'magma'
    scat = pp.scatter(scatter_data(), cbar=True, cmap=name)
    assert scat._view.colormapper.cmap.name == name


def test_scatter_with_size():
    a = scatter_data()
    a.coords['s'] = sc.abs(a.coords['x']) * 5
    pp.scatter(a, size='s')


def test_scatter_with_size_and_cbar():
    a = scatter_data()
    a.coords['s'] = sc.abs(a.coords['x']) * 5
    pp.scatter(a, size='s', cbar=True)


def test_scatter_with_masks():
    a = scatter_data()
    a.masks['m'] = a.coords['x'] > sc.scalar(10, unit='m')
    pp.scatter(a)


def test_scatter_flattens_2d_data():
    pp.scatter(data_array(ndim=2), x='xx', y='yy', cbar=True)


def test_scatter_with_norm():
    a = scatter_data()
    scat = pp.scatter(a, cbar=True, norm='linear')
    assert scat._view.colormapper.norm == 'linear'
    scat = pp.scatter(a, cbar=True, norm='log')
    assert scat._view.colormapper.norm == 'log'


def test_scatter_log_axes():
    a = scatter_data()
    scat = pp.scatter(a)
    assert scat._view.canvas.xscale == 'linear'
    assert scat._view.canvas.yscale == 'linear'
    scat = pp.scatter(a, scale={'x': 'log', 'y': 'log'})
    assert scat._view.canvas.xscale == 'log'
    assert scat._view.canvas.yscale == 'log'
