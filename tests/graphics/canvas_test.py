# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

from functools import partial

import pytest

from plopp import Node
from plopp.data import data1d, data2d, data_array, scatter
from plopp.graphics import imagefigure, linefigure, scatter3dfigure, scatterfigure
from plopp.testing import Case, to_params

CASES = to_params(
    [
        Case(('2d', 'mpl-static'), linefigure, data1d),
        Case(('2d', 'mpl-interactive'), linefigure, data1d),
        Case(('2d', 'plotly'), linefigure, data1d),
        Case(('2d', 'mpl-static'), partial(imagefigure, cbar=True), data2d),
        Case(('2d', 'mpl-interactive'), partial(imagefigure, cbar=True), data2d),
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
CASES1D = [c for c in CASES if c.values[0].figure is linefigure]
CASESNO3D = [c for c in CASES if c.values[0].figure is not scatter3dfigure]
CASES1DINTERACTIVE = [c for c in CASES1D if c.values[0].backend[1] != 'mpl-static']


@pytest.mark.parametrize('case', CASES)
def test_empty(case):
    case.set_backend()
    canvas = case.figure().canvas
    assert canvas.empty


@pytest.mark.parametrize('case', CASES)
def test_title(case):
    case.set_backend()
    da = case.data()
    title = 'test title'
    canvas = case.figure(Node(da), title=title).canvas
    assert canvas.title == title
    canvas = case.figure(Node(da)).canvas
    assert not canvas.title
    canvas.title = title + '2'
    assert canvas.title == title + '2'


@pytest.mark.parametrize('case', CASES)
def test_xlabel(case):
    case.set_backend()
    da = case.data()
    xlabel = 'test xlabel'
    canvas = case.figure(Node(da)).canvas
    assert canvas.xlabel == 'x [m]'
    canvas.xlabel = xlabel
    assert canvas.xlabel == xlabel


@pytest.mark.parametrize('case', CASES)
def test_ylabel(case):
    case.set_backend()
    da = case.data()
    ylabel = 'test ylabel'
    canvas = case.figure(Node(da)).canvas
    canvas.ylabel = ylabel
    assert canvas.ylabel == ylabel


@pytest.mark.parametrize('case', CASES)
def test_xscale(case):
    case.set_backend()
    da = case.data()
    canvas = case.figure(Node(da)).canvas
    assert canvas.xscale == 'linear'
    canvas.xscale = 'log'
    assert canvas.xscale == 'log'


@pytest.mark.parametrize('case', CASES)
def test_yscale(case):
    case.set_backend()
    da = case.data()
    canvas = case.figure(Node(da)).canvas
    assert canvas.yscale == 'linear'
    canvas.yscale = 'log'
    assert canvas.yscale == 'log'


@pytest.mark.parametrize('case', CASES)
def test_xmin(case):
    case.set_backend()
    da = case.data()
    canvas = case.figure(Node(da)).canvas
    canvas.xmin = -123.0
    assert canvas.xmin == -123.0


@pytest.mark.parametrize('case', CASES)
def test_xmax(case):
    case.set_backend()
    da = case.data()
    canvas = case.figure(Node(da)).canvas
    canvas.xmax = 34.0
    assert canvas.xmax == 34.0


@pytest.mark.parametrize('case', CASES)
def test_ymin(case):
    case.set_backend()
    da = case.data()
    canvas = case.figure(Node(da)).canvas
    canvas.ymin = -123.0
    assert canvas.ymin == -123.0


@pytest.mark.parametrize('case', CASES)
def test_ymax(case):
    case.set_backend()
    da = case.data()
    canvas = case.figure(Node(da)).canvas
    canvas.ymax = 34.0
    assert canvas.ymax == 34.0


@pytest.mark.parametrize('case', CASES)
def test_xrange(case):
    case.set_backend()
    da = case.data()
    canvas = case.figure(Node(da)).canvas
    canvas.xrange = (-123.0, 34.0)
    assert canvas.xrange == (-123.0, 34.0)


@pytest.mark.parametrize('case', CASES)
def test_yrange(case):
    case.set_backend()
    da = case.data()
    canvas = case.figure(Node(da)).canvas
    canvas.yrange = (-123.0, 34.0)
    assert canvas.yrange == (-123.0, 34.0)


@pytest.mark.parametrize('case', CASESNO3D)
def test_logx(case):
    case.set_backend()
    da = case.data()
    canvas = case.figure(Node(da)).canvas
    assert canvas.xscale == 'linear'
    assert canvas.yscale == 'linear'
    canvas.logx()
    assert canvas.xscale == 'log'
    assert canvas.yscale == 'linear'


@pytest.mark.parametrize('case', CASESNO3D)
def test_logy(case):
    case.set_backend()
    da = case.data()
    canvas = case.figure(Node(da)).canvas
    assert canvas.xscale == 'linear'
    assert canvas.yscale == 'linear'
    canvas.logy()
    assert canvas.xscale == 'linear'
    assert canvas.yscale == 'log'


@pytest.mark.parametrize('case', CASES1DINTERACTIVE)
def test_logx_1d_toolbar_button_state_agrees_with_kwarg(case):
    case.set_backend()
    da = case.data()
    fig = case.figure(Node(da), scale={'x': 'log'})
    assert fig.toolbar['logx'].value


@pytest.mark.parametrize('case', CASES1DINTERACTIVE)
def test_logx_1d_toolbar_button_toggles_xscale(case):
    case.set_backend()
    da = case.data()
    fig = case.figure(Node(da))
    assert fig.canvas.xscale == 'linear'
    fig.toolbar['logx'].value = True
    assert fig.canvas.xscale == 'log'


@pytest.mark.parametrize('case', CASES1DINTERACTIVE)
def test_logy_1d_toolbar_button_state_agrees_with_kwarg(case):
    case.set_backend()
    da = case.data()
    fig = case.figure(Node(da), norm='log')
    assert fig.toolbar['logy'].value


@pytest.mark.parametrize('case', CASES1DINTERACTIVE)
def test_logy_1d_toolbar_button_toggles_yscale(case):
    case.set_backend()
    da = case.data()
    fig = case.figure(Node(da))
    assert fig.canvas.yscale == 'linear'
    fig.toolbar['logy'].value = True
    assert fig.canvas.yscale == 'log'


@pytest.mark.usefixtures('_use_ipympl')
def test_logxy_2d_toolbar_buttons_state_agrees_with_kwarg():
    da = data_array(ndim=2)
    fig = da.plot(scale={'x': 'log', 'y': 'log'})
    assert fig.toolbar['logx'].value
    assert fig.toolbar['logy'].value


@pytest.mark.usefixtures('_use_ipympl')
def test_logxy_2d_toolbar_buttons_toggles_xyscale():
    da = data_array(ndim=2)
    fig = da.plot()
    assert fig.canvas.xscale == 'linear'
    assert fig.canvas.yscale == 'linear'
    fig.toolbar['logx'].value = True
    assert fig.canvas.xscale == 'log'
    assert fig.canvas.yscale == 'linear'
    fig.toolbar['logy'].value = True
    assert fig.canvas.xscale == 'log'
    assert fig.canvas.yscale == 'log'
