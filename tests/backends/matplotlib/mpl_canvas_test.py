# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import os
import tempfile

import pytest
import scipp as sc

from plopp.backends.matplotlib.canvas import Canvas


def test_creation():
    title = 'My canvas'
    canvas = Canvas(title=title)
    assert canvas.ax.get_title() == title
    assert canvas.ax.get_xscale() == 'linear'
    assert canvas.ax.get_yscale() == 'linear'


def test_logx():
    canvas = Canvas()
    assert canvas.ax.get_xscale() == 'linear'
    assert canvas.xscale == 'linear'
    canvas.logx()
    assert canvas.ax.get_xscale() == 'log'
    assert canvas.xscale == 'log'
    canvas.logx()
    assert canvas.ax.get_xscale() == 'linear'
    assert canvas.xscale == 'linear'


def test_logy():
    canvas = Canvas()
    assert canvas.ax.get_yscale() == 'linear'
    assert canvas.yscale == 'linear'
    canvas.logy()
    assert canvas.ax.get_yscale() == 'log'
    assert canvas.yscale == 'log'
    canvas.logy()
    assert canvas.ax.get_yscale() == 'linear'
    assert canvas.yscale == 'linear'


def test_crop():
    canvas = Canvas()
    canvas.xunit = 'm'
    canvas.yunit = 'm'
    xmin = sc.scalar(2.1, unit='m')
    xmax = sc.scalar(102.0, unit='m')
    ymin = sc.scalar(5.5, unit='m')
    ymax = sc.scalar(22.3, unit='m')
    canvas.crop(x={
        'min': xmin,
        'max': xmax,
    }, y={
        'min': ymin,
        'max': ymax,
    })
    assert canvas.ax.get_xlim() == (xmin.value, xmax.value)
    assert canvas.ax.get_ylim() == (ymin.value, ymax.value)


def test_crop_unit_conversion():
    canvas = Canvas()
    canvas.xunit = 'cm'
    canvas.yunit = 'cm'
    xmin = sc.scalar(2.1, unit='m')
    xmax = sc.scalar(3.3, unit='m')
    canvas.crop(x={'min': xmin, 'max': xmax})
    assert canvas.ax.get_xlim() == (210., 330.)


def test_crop_no_variable():
    canvas = Canvas()
    canvas.xunit = 'm'
    canvas.yunit = 'm'
    xmin = 2.1
    xmax = 102.0
    ymin = 5.5
    ymax = 22.3
    canvas.crop(x={
        'min': xmin,
        'max': xmax,
    }, y={
        'min': ymin,
        'max': ymax,
    })
    assert canvas.ax.get_xlim() == (xmin, xmax)
    assert canvas.ax.get_ylim() == (ymin, ymax)


@pytest.mark.parametrize('ext', ['jpg', 'png', 'pdf', 'svg'])
def test_save_to_disk(ext):
    canvas = Canvas()
    with tempfile.TemporaryDirectory() as path:
        fname = os.path.join(path, f'plopp_fig.{ext}')
        canvas.save(filename=fname)
        assert os.path.isfile(fname)


def test_save_to_disk_with_bad_extension_raises():
    canvas = Canvas()
    with pytest.raises(ValueError):
        canvas.save(filename='plopp_fig.txt')
