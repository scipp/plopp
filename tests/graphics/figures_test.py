# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

from collections.abc import Callable
from dataclasses import dataclass
from functools import partial

import pytest
import scipp as sc

from plopp import Node
from plopp.data import data1d, data2d, scatter
from plopp.graphics import imagefigure, linefigure, scatter3dfigure, scatterfigure
from plopp.testing import Case, to_params


@dataclass
class FigureAndData:
    figure: Callable
    data: Callable


PLOTCASES = to_params(
    [
        Case(('2d', 'mpl-static'), linefigure, data1d),
        Case(('2d', 'mpl-interactive'), linefigure, data1d),
        Case(('2d', 'plotly'), linefigure, data1d),
        Case(('2d', 'mpl-static'), partial(imagefigure, cbar=True), data2d),
        Case(('2d', 'mpl-interactive'), partial(imagefigure, cbar=True), data2d),
    ]
)

SCATTERCASES = to_params(
    [
        Case(
            ('2d', 'mpl-static'),
            partial(scatterfigure, x='x', y='y', cbar=True),
            scatter,
        ),
        Case(
            ('2d', 'mpl-interactive'),
            partial(scatterfigure, x='x', y='y', cbar=True),
            scatter,
        ),
        Case(
            ('3d', 'pythreejs'),
            partial(scatter3dfigure, x='x', y='y', z='z', cbar=True),
            scatter,
        ),
    ]
)


ALLCASES = PLOTCASES + SCATTERCASES


@pytest.mark.parametrize('case', ALLCASES)
def test_empty(case):
    case.set_backend()
    fig = case.figure()
    assert len(fig.artists) == 0


@pytest.mark.parametrize('case', ALLCASES)
def test_creation(case):
    case.set_backend()
    da = case.data()
    fig = case.figure(Node(da))
    [artist] = fig.artists.values()
    assert sc.identical(artist._data, da)


@pytest.mark.parametrize('case', ALLCASES)
def test_update(case):
    case.set_backend()
    fig = case.figure()
    assert len(fig.artists) == 0
    da = case.data()
    key = 'data_update'
    fig.update({key: da})
    assert sc.identical(fig.artists[key]._data, da)


@pytest.mark.parametrize('case', PLOTCASES)
def test_raises_for_new_data_with_incompatible_dimension(case):
    case.set_backend()
    x = case.data()
    y = x.rename(x='other')
    with pytest.raises(KeyError):
        case.figure(Node(x), Node(y))


@pytest.mark.parametrize('case', SCATTERCASES)
def test_raises_for_new_data_with_incompatible_coordinate(case):
    case.set_backend()
    a = case.data()
    b = case.data()
    b.coords['t'] = b.coords.pop('x')
    with pytest.raises(KeyError):
        case.figure(Node(a), Node(b))


@pytest.mark.parametrize('case', ALLCASES)
def test_raises_for_new_data_with_incompatible_unit(case):
    case.set_backend()
    a = case.data()
    b = a * a
    with pytest.raises(sc.UnitError):
        case.figure(Node(a), Node(b))


@pytest.mark.parametrize('case', ALLCASES)
def test_raises_for_new_data_with_incompatible_coord_unit(case):
    case.set_backend()
    a = case.data()
    b = a.copy()
    b.coords['x'] = a.coords['x'] * a.coords['x']
    with pytest.raises(sc.UnitError):
        case.figure(Node(a), Node(b))


@pytest.mark.parametrize('case', ALLCASES)
def test_converts_new_data_units(case):
    case.set_backend()
    a = case.data(unit='m')
    b = case.data(unit='cm')
    fig = case.figure(Node(a), Node(b))
    [art_a, art_b] = fig.artists.values()
    assert sc.identical(art_a._data, a)
    assert sc.identical(art_b._data, b.to(unit='m'))


@pytest.mark.parametrize('case', ALLCASES)
def test_converts_new_data_coordinate_units(case):
    case.set_backend()
    a = case.data()
    b = case.data()
    b.coords['x'] = b.coords['x'].copy()
    b.coords['x'].unit = 'cm'
    fig = case.figure(Node(a), Node(b))
    [art_a, art_b] = fig.artists.values()
    assert sc.identical(art_a._data, a)
    c = b.copy()
    c.coords['x'] = c.coords['x'].to(unit='m')
    assert sc.identical(art_b._data, c)


@pytest.mark.parametrize('case', ALLCASES)
def test_converts_new_data_units_integers(case):
    case.set_backend()
    a = case.data(unit='m').to(dtype=int)
    b = case.data(unit='m').to(unit='cm', dtype=int)
    fig = case.figure(Node(a), Node(b))
    [art_a, art_b] = fig.artists.values()
    assert sc.identical(art_a._data, a)
    assert sc.identical(art_b._data, b.to(unit='m', dtype=float))
