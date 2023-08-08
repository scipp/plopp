# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import os
import tempfile

import pytest

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
