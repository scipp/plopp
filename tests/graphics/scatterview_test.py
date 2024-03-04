# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import pytest
import scipp as sc

from plopp import Node
from plopp.data.testing import scatter as scatter_data
from plopp.graphics.scatterview import ScatterView


def test_creation():
    da = scatter_data()
    fig = ScatterView(Node(da), x='x', y='y')
    assert len(fig.artists) == 1
    key = list(fig.artists.keys())[0]
    assert sc.identical(fig.artists[key]._data, da)


def test_update():
    da = scatter_data()
    fig = ScatterView(Node(da), x='x', y='y')
    assert len(fig.artists) == 1
    key = list(fig.artists.keys())[0]
    fig.update({key: da * 3.3})
    assert sc.identical(fig.artists[key]._data, da * 3.3)


def test_raises_for_new_data_with_incompatible_coordinate():
    a = scatter_data()
    b = scatter_data()
    b.coords['t'] = b.coords.pop('x')
    with pytest.raises(KeyError):
        ScatterView(Node(a), Node(b), x='x', y='y')


def test_raises_for_new_data_with_incompatible_unit():
    a = scatter_data()
    b = a * a
    with pytest.raises(sc.UnitError):
        ScatterView(Node(a), Node(b), x='x', y='y', cbar=True)


def test_raises_for_new_data_with_incompatible_coord_unit():
    a = scatter_data()
    b = a.copy()
    b.coords['x'] = a.coords['x'] * a.coords['x']
    with pytest.raises(sc.UnitError):
        ScatterView(Node(a), Node(b), x='x', y='y')


def test_converts_new_data_units():
    a = scatter_data()
    a.unit = 'm'
    b = scatter_data()
    b.unit = 'cm'
    anode = Node(a)
    bnode = Node(b)
    fig = ScatterView(anode, bnode, x='x', y='y', cbar=True)
    assert sc.identical(fig.artists[anode.id]._data, a)
    assert sc.identical(fig.artists[bnode.id]._data, b.to(unit='m'))


def test_converts_new_data_coordinate_units():
    a = scatter_data()
    b = scatter_data()
    xcoord = b.coords['x'].copy()
    xcoord.unit = 'cm'
    b.coords['x'] = xcoord
    anode = Node(a)
    bnode = Node(b)
    fig = ScatterView(anode, bnode, x='x', y='y')
    assert sc.identical(fig.artists[anode.id]._data, a)
    c = b.copy()
    c.coords['x'] = c.coords['x'].to(unit='m')
    assert sc.identical(fig.artists[bnode.id]._data, c)
