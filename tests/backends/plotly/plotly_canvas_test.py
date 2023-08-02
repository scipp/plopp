# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import os
import tempfile

import pytest

from plopp.backends.plotly.canvas import Canvas

pytest.importorskip("plotly")


def test_creation():
    title = 'My canvas'
    canvas = Canvas(title=title)
    assert canvas.title == title


def test_logx():
    canvas = Canvas()
    canvas.logx()
    assert canvas.xscale == 'log'
    canvas.logx()
    assert canvas.xscale == 'linear'


def test_logy():
    canvas = Canvas()
    canvas.logy()
    assert canvas.yscale == 'log'
    canvas.logy()
    assert canvas.yscale == 'linear'


@pytest.mark.parametrize('ext', ['jpg', 'png', 'pdf', 'svg', 'html'])
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
