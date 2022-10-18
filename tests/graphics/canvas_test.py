# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.data import dense_data_array
from plopp.graphics.canvas import Canvas
from plopp.graphics.line import Line
from plopp.graphics.mesh import Mesh
from plopp import input_node
import scipp as sc
from common import make_axes
import pytest


def test_creation():
    title = 'My canvas'
    canvas = Canvas(ax=make_axes(), title=title)
    assert canvas.ax.get_title() == title
    assert canvas.ax.get_xscale() == 'linear'
    assert canvas.ax.get_yscale() == 'linear'


def test_logx():
    canvas = Canvas(ax=make_axes())
    assert canvas.ax.get_xscale() == 'linear'
    assert canvas.xscale == 'linear'
    canvas.logx()
    assert canvas.ax.get_xscale() == 'log'
    assert canvas.xscale == 'log'
    canvas.logx()
    assert canvas.ax.get_xscale() == 'linear'
    assert canvas.xscale == 'linear'


def test_logy():
    canvas = Canvas(ax=make_axes())
    assert canvas.ax.get_yscale() == 'linear'
    assert canvas.yscale == 'linear'
    canvas.logy()
    assert canvas.ax.get_yscale() == 'log'
    assert canvas.yscale == 'log'
    canvas.logy()
    assert canvas.ax.get_yscale() == 'linear'
    assert canvas.yscale == 'linear'


def test_crop():
    canvas = Canvas(ax=make_axes())
    xmin = sc.scalar(2.1, unit='m')
    xmax = sc.scalar(102.0, unit='m')
    ymin = sc.scalar(5.5, unit='m')
    ymax = sc.scalar(22.3, unit='m')
    canvas.crop(x={
        'min': xmin,
        'max': xmax,
        'unit': 'm'
    },
                y={
                    'min': ymin,
                    'max': ymax,
                    'unit': 'm'
                })
    assert canvas.ax.get_xlim() == (xmin.value, xmax.value)
    assert canvas.ax.get_ylim() == (ymin.value, ymax.value)


def test_crop_unit_conversion():
    canvas = Canvas(ax=make_axes())
    xmin = sc.scalar(2.1, unit='m')
    xmax = sc.scalar(3.3, unit='m')
    canvas.crop(x={'min': xmin, 'max': xmax, 'unit': 'cm'})
    assert canvas.ax.get_xlim() == (210., 330.)
