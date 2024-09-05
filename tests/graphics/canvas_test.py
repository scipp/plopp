# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

from collections.abc import Callable
from dataclasses import dataclass
from functools import partial

import pytest

from plopp import Node, backends
from plopp.data import data1d, data2d, data_array, scatter
from plopp.graphics import imagefigure, linefigure, scatter3dfigure, scatterfigure


@dataclass
class FigureAndData:
    figure: Callable
    data: Callable


def backend_linefigure(*args, backend=None, **kwargs):
    backends['2d'] = backend
    return linefigure(*args, **kwargs)


CASES = [
    FigureAndData(partial(backend_linefigure, backend='matplotlib'), data1d),
    FigureAndData(partial(backend_linefigure, backend='plotly'), data1d),
    FigureAndData(partial(imagefigure, cbar=True), data2d),
    FigureAndData(partial(scatterfigure, x='x', y='y', cbar=True), scatter),
    FigureAndData(partial(scatter3dfigure, x='x', y='y', z='z', cbar=True), scatter),
]

CASES1D = CASES[:2]
CASESNO3D = CASES[:4]


@pytest.mark.parametrize('case', CASES)
def test_empty(case):
    canvas = case.figure().canvas
    assert canvas.empty


@pytest.mark.parametrize('case', CASES)
def test_title(case):
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
    da = case.data()
    xlabel = 'test xlabel'
    canvas = case.figure(Node(da)).canvas
    assert canvas.xlabel == 'x [m]'
    canvas.xlabel = xlabel
    assert canvas.xlabel == xlabel


@pytest.mark.parametrize('case', CASES)
def test_ylabel(case):
    da = case.data()
    ylabel = 'test ylabel'
    canvas = case.figure(Node(da)).canvas
    canvas.ylabel = ylabel
    assert canvas.ylabel == ylabel


@pytest.mark.parametrize('case', CASES)
def test_xscale(case):
    da = case.data()
    canvas = case.figure(Node(da)).canvas
    assert canvas.xscale == 'linear'
    canvas.xscale = 'log'
    assert canvas.xscale == 'log'


@pytest.mark.parametrize('case', CASES)
def test_yscale(case):
    da = case.data()
    canvas = case.figure(Node(da)).canvas
    assert canvas.yscale == 'linear'
    canvas.yscale = 'log'
    assert canvas.yscale == 'log'


@pytest.mark.parametrize('case', CASES)
def test_xmin(case):
    da = case.data()
    canvas = case.figure(Node(da)).canvas
    canvas.xmin = -123.0
    assert canvas.xmin == -123.0


@pytest.mark.parametrize('case', CASES)
def test_xmax(case):
    da = case.data()
    canvas = case.figure(Node(da)).canvas
    canvas.xmax = 34.0
    assert canvas.xmax == 34.0


@pytest.mark.parametrize('case', CASES)
def test_ymin(case):
    da = case.data()
    canvas = case.figure(Node(da)).canvas
    canvas.ymin = -123.0
    assert canvas.ymin == -123.0


@pytest.mark.parametrize('case', CASES)
def test_ymax(case):
    da = case.data()
    canvas = case.figure(Node(da)).canvas
    canvas.ymax = 34.0
    assert canvas.ymax == 34.0


@pytest.mark.parametrize('case', CASES)
def test_xrange(case):
    da = case.data()
    canvas = case.figure(Node(da)).canvas
    canvas.xrange = (-123.0, 34.0)
    assert canvas.xrange == (-123.0, 34.0)


@pytest.mark.parametrize('case', CASES)
def test_yrange(case):
    da = case.data()
    canvas = case.figure(Node(da)).canvas
    canvas.yrange = (-123.0, 34.0)
    assert canvas.yrange == (-123.0, 34.0)


@pytest.mark.parametrize('case', CASESNO3D)
def test_logx(case):
    da = case.data()
    canvas = case.figure(Node(da)).canvas
    assert canvas.xscale == 'linear'
    assert canvas.yscale == 'linear'
    canvas.logx()
    assert canvas.xscale == 'log'
    assert canvas.yscale == 'linear'


@pytest.mark.parametrize('case', CASESNO3D)
def test_logy(case):
    da = case.data()
    canvas = case.figure(Node(da)).canvas
    assert canvas.xscale == 'linear'
    assert canvas.yscale == 'linear'
    canvas.logy()
    assert canvas.xscale == 'linear'
    assert canvas.yscale == 'log'


@pytest.mark.usefixtures('_use_ipympl')
@pytest.mark.parametrize('case', CASES1D)
def test_logx_1d_toolbar_button_state_agrees_with_kwarg(case):
    da = case.data()
    fig = case.figure(Node(da), scale={'x': 'log'})
    assert fig.toolbar['logx'].value


@pytest.mark.usefixtures('_use_ipympl')
@pytest.mark.parametrize('case', CASES1D)
def test_logx_1d_toolbar_button_toggles_xscale(case):
    da = case.data()
    fig = case.figure(Node(da))
    assert fig.canvas.xscale == 'linear'
    fig.toolbar['logx'].value = True
    assert fig.canvas.xscale == 'log'


@pytest.mark.usefixtures('_use_ipympl')
@pytest.mark.parametrize('case', CASES1D)
def test_logy_1d_toolbar_button_state_agrees_with_kwarg(case):
    da = case.data()
    fig = case.figure(Node(da), norm='log')
    assert fig.toolbar['logy'].value


@pytest.mark.usefixtures('_use_ipympl')
@pytest.mark.parametrize('case', CASES1D)
def test_logy_1d_toolbar_button_toggles_yscale(case):
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
