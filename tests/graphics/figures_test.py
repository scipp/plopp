# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

from functools import partial

import pytest
import scipp as sc

from plopp import Node
from plopp.data import data1d, data2d, scatter
from plopp.graphics import imagefigure, linefigure, scatter3dfigure, scatterfigure

PLOTCASES = {
    "linefigure-mpl-static": (('2d', 'mpl-static'), linefigure, data1d),
    "linefigure-mpl-interactive": (('2d', 'mpl-interactive'), linefigure, data1d),
    "linefigure-plotly": (('2d', 'plotly'), linefigure, data1d),
    "imagefigure-mpl-static": (
        ('2d', 'mpl-static'),
        partial(imagefigure, cbar=True),
        data2d,
    ),
    "imagefigure-mpl-interactive": (
        ('2d', 'mpl-interactive'),
        partial(imagefigure, cbar=True),
        data2d,
    ),
}

SCATTERCASES = {
    "scatterfigure-mpl-static": (
        ('2d', 'mpl-static'),
        partial(scatterfigure, x='x', y='y', cbar=True),
        scatter,
    ),
    "scatterfigure-mpl-interactive": (
        ('2d', 'mpl-interactive'),
        partial(scatterfigure, x='x', y='y', cbar=True),
        scatter,
    ),
    "scatter3dfigure-pythreejs": (
        ('3d', 'pythreejs'),
        partial(scatter3dfigure, x='x', y='y', z='z', cbar=True),
        scatter,
    ),
}


ALLCASES = {**PLOTCASES, **SCATTERCASES}


@pytest.mark.parametrize("backend,figure,data", ALLCASES.values(), ids=ALLCASES.keys())
class TestFiguresAllCases:
    def test_empty(self, set_backend, backend, figure, data):
        fig = figure()
        assert len(fig.artists) == 0

    def test_creation(self, set_backend, backend, figure, data):
        da = data()
        fig = figure(Node(da))
        [artist] = fig.artists.values()
        assert sc.identical(artist._data, da)

    def test_update(self, set_backend, backend, figure, data):
        fig = figure()
        assert len(fig.artists) == 0
        da = data()
        key = 'data_update'
        fig.update({key: da})
        assert sc.identical(fig.artists[key]._data, da)

    def test_raises_for_new_data_with_incompatible_unit(
        self, set_backend, backend, figure, data
    ):
        a = data()
        b = a * a
        with pytest.raises(sc.UnitError):
            figure(Node(a), Node(b))

    def test_raises_for_new_data_with_incompatible_coord_unit(
        self, set_backend, backend, figure, data
    ):
        a = data()
        b = a.copy()
        b.coords['x'] = a.coords['x'] * a.coords['x']
        with pytest.raises(sc.UnitError):
            figure(Node(a), Node(b))

    def test_converts_new_data_units(self, set_backend, backend, figure, data):
        a = data(unit='m')
        b = data(unit='cm')
        fig = figure(Node(a), Node(b))
        [art_a, art_b] = fig.artists.values()
        assert sc.identical(art_a._data, a)
        assert sc.identical(art_b._data, b.to(unit='m'))

    def test_converts_new_data_coordinate_units(
        self, set_backend, backend, figure, data
    ):
        a = data()
        b = data()
        b.coords['x'] = b.coords['x'].copy()
        b.coords['x'].unit = 'cm'
        fig = figure(Node(a), Node(b))
        [art_a, art_b] = fig.artists.values()
        assert sc.identical(art_a._data, a)
        c = b.copy()
        c.coords['x'] = c.coords['x'].to(unit='m')
        assert sc.identical(art_b._data, c)

    def test_converts_new_data_units_integers(self, set_backend, backend, figure, data):
        a = data(unit='m').to(dtype=int)
        b = data(unit='m').to(unit='cm', dtype=int)
        fig = figure(Node(a), Node(b))
        [art_a, art_b] = fig.artists.values()
        assert sc.identical(art_a._data, a)
        assert sc.identical(art_b._data, b.to(unit='m', dtype=float))


@pytest.mark.parametrize(
    ("backend", "figure", "data"), PLOTCASES.values(), ids=PLOTCASES.keys()
)
def test_raises_for_new_data_with_incompatible_dimension(
    set_backend, backend, figure, data
):
    x = data()
    y = x.rename(x='other')
    with pytest.raises(KeyError):
        figure(Node(x), Node(y))


@pytest.mark.parametrize(
    ("backend", "figure", "data"), SCATTERCASES.values(), ids=SCATTERCASES.keys()
)
def test_raises_for_new_data_with_incompatible_coordinate(
    set_backend, backend, figure, data
):
    a = data()
    b = data()
    b.coords['t'] = b.coords.pop('x')
    with pytest.raises(KeyError):
        figure(Node(a), Node(b))
