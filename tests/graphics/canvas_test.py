# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)
from dataclasses import dataclass
from functools import partial
from typing import Callable

import pytest

from plopp import Node, backends
from plopp.data import data1d, data2d, scatter
from plopp.graphics import imagefigure, linefigure, scatterfigure


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
]


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


@pytest.mark.parametrize('case', CASES)
def test_logx(case):
    da = case.data()
    canvas = case.figure(Node(da)).canvas
    assert canvas.xscale == 'linear'
    assert canvas.yscale == 'linear'
    canvas.logx()
    assert canvas.xscale == 'log'
    assert canvas.yscale == 'linear'


@pytest.mark.parametrize('case', CASES)
def test_logy(case):
    da = case.data()
    canvas = case.figure(Node(da)).canvas
    assert canvas.xscale == 'linear'
    assert canvas.yscale == 'linear'
    canvas.logy()
    assert canvas.xscale == 'linear'
    assert canvas.yscale == 'log'
