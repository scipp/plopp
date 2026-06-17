# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

from functools import partial

import pytest

from plopp import Node
from plopp.data import data1d, data2d, data_array, scatter
from plopp.graphics import imagefigure, linefigure, scatter3dfigure, scatterfigure

CASES = {
    "linefigure-mpl-static": (('2d', 'mpl-static'), linefigure, data1d),
    "linefigure-mpl-interactive": (('2d', 'mpl-interactive'), linefigure, data1d),
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


@pytest.mark.parametrize(
    ("backend", "figure", "data"), CASES.values(), ids=CASES.keys()
)
class TestCanvasAllCases:
    def test_empty(self, set_backend, backend, figure, data):
        canvas = figure().canvas
        assert canvas.empty

    def test_title(self, set_backend, backend, figure, data):
        da = data()
        title = 'test title'
        canvas = figure(Node(da), title=title).canvas
        assert canvas.title == title
        canvas = figure(Node(da)).canvas
        assert not canvas.title
        canvas.title = title + '2'
        assert canvas.title == title + '2'

    def test_xlabel(self, set_backend, backend, figure, data):
        da = data()
        xlabel = 'test xlabel'
        canvas = figure(Node(da)).canvas
        assert canvas.xlabel == 'x [m]'
        canvas.xlabel = xlabel
        assert canvas.xlabel == xlabel

    def test_ylabel(self, set_backend, backend, figure, data):
        da = data()
        ylabel = 'test ylabel'
        canvas = figure(Node(da)).canvas
        canvas.ylabel = ylabel
        assert canvas.ylabel == ylabel

    def test_xscale(self, set_backend, backend, figure, data):
        da = data()
        canvas = figure(Node(da)).canvas
        assert canvas.xscale == 'linear'
        canvas.xscale = 'log'
        assert canvas.xscale == 'log'

    def test_yscale(self, set_backend, backend, figure, data):
        da = data()
        canvas = figure(Node(da)).canvas
        assert canvas.yscale == 'linear'
        canvas.yscale = 'log'
        assert canvas.yscale == 'log'

    def test_xmin(self, set_backend, backend, figure, data):
        da = data()
        canvas = figure(Node(da)).canvas
        canvas.xmin = -123.0
        assert canvas.xmin == -123.0

    def test_xmax(self, set_backend, backend, figure, data):
        da = data()
        canvas = figure(Node(da)).canvas
        canvas.xmax = 34.0
        assert canvas.xmax == 34.0

    def test_ymin(self, set_backend, backend, figure, data):
        da = data()
        canvas = figure(Node(da)).canvas
        canvas.ymin = -123.0
        assert canvas.ymin == -123.0

    def test_ymax(self, set_backend, backend, figure, data):
        da = data()
        canvas = figure(Node(da)).canvas
        canvas.ymax = 34.0
        assert canvas.ymax == 34.0

    def test_xrange(self, set_backend, backend, figure, data):
        da = data()
        canvas = figure(Node(da)).canvas
        canvas.xrange = (-123.0, 34.0)
        assert canvas.xrange == (-123.0, 34.0)

    def test_yrange(self, set_backend, backend, figure, data):
        da = data()
        canvas = figure(Node(da)).canvas
        canvas.yrange = (-123.0, 34.0)
        assert canvas.yrange == (-123.0, 34.0)


CASESNO3D = {k: c for k, c in CASES.items() if c[0][0] != "3d"}


@pytest.mark.parametrize(
    ("backend", "figure", "data"), CASESNO3D.values(), ids=CASESNO3D.keys()
)
class TestCanvasNo3d:
    def test_toggle_logx(self, set_backend, backend, figure, data):
        da = data()
        canvas = figure(Node(da)).canvas
        assert canvas.xscale == 'linear'
        assert canvas.yscale == 'linear'
        canvas.toggle_logx()
        assert canvas.xscale == 'log'
        assert canvas.yscale == 'linear'

    def test_toggle_logy(self, set_backend, backend, figure, data):
        da = data()
        canvas = figure(Node(da)).canvas
        assert canvas.xscale == 'linear'
        assert canvas.yscale == 'linear'
        canvas.toggle_logy()
        assert canvas.xscale == 'linear'
        assert canvas.yscale == 'log'

    def test_xrange_order_preserved(self, set_backend, backend, figure, data):
        da = data()
        fig = figure(Node(da))
        fig.canvas.xrange = (52.0, -5.0)
        fig.view.autoscale()
        new_range = fig.canvas.xrange
        assert new_range[0] > new_range[1]

    def test_yrange_order_preserved(self, set_backend, backend, figure, data):
        da = data()
        fig = figure(Node(da))
        fig.canvas.yrange = (61.0, -6.6)
        fig.view.autoscale()
        new_range = fig.canvas.yrange
        assert new_range[0] > new_range[1]
