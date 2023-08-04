# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import pytest
import scipp as sc

from plopp import Node
from plopp.data.testing import scatter
from plopp.graphics.scatter3dview import Scatter3dView


def test_creation():
    da = scatter()
    fig = Scatter3dView(Node(da), x='x', y='y', z='z')
    assert len(fig.artists) == 1
    key = list(fig.artists.keys())[0]
    assert sc.identical(fig.artists[key]._data, da)


def test_update():
    da = scatter()
    fig = Scatter3dView(Node(da), x='x', y='y', z='z')
    assert len(fig.artists) == 1
    key = list(fig.artists.keys())[0]
    fig.update(da * 3.3, key=key)
    assert sc.identical(fig.artists[key]._data, da * 3.3)


def test_log_norm():
    da = scatter()
    fig = Scatter3dView(Node(da), x='x', y='y', z='z', norm='log')
    assert fig.colormapper.norm == 'log'


def test_raises_for_new_data_with_incompatible_coordinate():
    a = scatter()
    b = scatter()
    b.coords['t'] = b.coords.pop('x')
    with pytest.raises(KeyError):
        Scatter3dView(Node(a), Node(b), x='x', y='y', z='z')


def test_raises_for_new_data_with_incompatible_unit():
    a = scatter()
    b = a * a
    with pytest.raises(sc.UnitError):
        Scatter3dView(Node(a), Node(b), x='x', y='y', z='z')


def test_raises_for_new_data_with_incompatible_coord_unit():
    a = scatter()
    b = a.copy()
    b.coords['x'] = a.coords['x'] * a.coords['x']
    with pytest.raises(sc.UnitError):
        Scatter3dView(Node(a), Node(b), x='x', y='y', z='z')


def test_converts_new_data_units():
    a = scatter()
    a.unit = 'm'
    b = scatter()
    b.unit = 'cm'
    anode = Node(a)
    bnode = Node(b)
    fig = Scatter3dView(anode, bnode, x='x', y='y', z='z')
    assert sc.identical(fig.artists[anode.id]._data, a)
    assert sc.identical(fig.artists[bnode.id]._data, b.to(unit='m'))


def test_converts_new_data_coordinate_units():
    a = scatter()
    b = scatter()
    xcoord = b.coords['x'].copy()
    xcoord.unit = 'cm'
    b.coords['x'] = xcoord
    anode = Node(a)
    bnode = Node(b)
    fig = Scatter3dView(anode, bnode, x='x', y='y', z='z')
    assert sc.identical(fig.artists[anode.id]._data, a)
    c = b.copy()
    c.coords['x'] = c.coords['x'].to(unit='m')
    assert sc.identical(fig.artists[bnode.id]._data, c)
