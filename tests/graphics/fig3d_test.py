# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.data.testing import scatter
from plopp.graphics.fig3d import Figure3d
from plopp.graphics.point_cloud import PointCloud
from plopp import input_node
import scipp as sc
import pytest


def test_creation():
    da = scatter()
    fig = Figure3d(input_node(da), x='x', y='y', z='z')
    assert len(fig.artists) == 1
    key = list(fig.artists.keys())[0]
    assert isinstance(fig.artists[key], PointCloud)
    assert sc.identical(fig.artists[key]._data, da)


def test_update():
    da = scatter()
    fig = Figure3d(input_node(da), x='x', y='y', z='z')
    assert len(fig.artists) == 1
    key = list(fig.artists.keys())[0]
    fig.update(da * 3.3, key=key)
    assert sc.identical(fig.artists[key]._data, da * 3.3)


def test_log_norm():
    da = scatter()
    fig = Figure3d(input_node(da), x='x', y='y', z='z', norm='log')
    assert fig.colormapper.norm == 'log'


def test_raises_for_new_data_with_incompatible_coordinate():
    a = scatter()
    b = scatter()
    b.coords['t'] = b.coords.pop('x')
    with pytest.raises(KeyError):
        Figure3d(input_node(a), input_node(b), x='x', y='y', z='z')


def test_raises_for_new_data_with_incompatible_unit():
    a = scatter()
    b = a * a
    with pytest.raises(sc.UnitError):
        Figure3d(input_node(a), input_node(b), x='x', y='y', z='z')


def test_raises_for_new_data_with_incompatible_coord_unit():
    a = scatter()
    b = a.copy()
    b.coords['x'] = a.coords['x'] * a.coords['x']
    with pytest.raises(sc.UnitError):
        Figure3d(input_node(a), input_node(b), x='x', y='y', z='z')


def test_converts_new_data_units():
    a = scatter()
    a.unit = 'm'
    b = scatter()
    b.unit = 'cm'
    anode = input_node(a)
    bnode = input_node(b)
    fig = Figure3d(anode, bnode, x='x', y='y', z='z')
    assert sc.identical(fig.artists[anode.id]._data, a)
    assert sc.identical(fig.artists[bnode.id]._data, b.to(unit='m'))


def test_converts_new_data_coordinate_units():
    a = scatter()
    b = scatter()
    xcoord = b.coords['x'].copy()
    xcoord.unit = 'cm'
    b.coords['x'] = xcoord
    anode = input_node(a)
    bnode = input_node(b)
    fig = Figure3d(anode, bnode, x='x', y='y', z='z')
    assert sc.identical(fig.artists[anode.id]._data, a)
    c = b.copy()
    c.coords['x'] = c.coords['x'].to(unit='m')
    assert sc.identical(fig.artists[bnode.id]._data, c)
