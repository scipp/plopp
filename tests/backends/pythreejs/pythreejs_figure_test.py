# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import os
import tempfile

import pytest

from plopp import input_node
from plopp.backends.pythreejs.figure import Figure
from plopp.data.testing import scatter
from plopp.graphics.figscatter3d import FigScatter3d


def test_log_norm_3d_toolbar_button():
    da = scatter()
    fig = Figure(input_node(da),
                 FigConstructor=FigScatter3d,
                 x='x',
                 y='y',
                 z='z',
                 norm='log')
    assert fig.toolbar['lognorm'].value


def test_save_to_html():
    da = scatter()
    fig = Figure(input_node(da),
                 FigConstructor=FigScatter3d,
                 x='x',
                 y='y',
                 z='z',
                 norm='log')
    with tempfile.TemporaryDirectory() as path:
        fname = os.path.join(path, 'plopp_fig3d.html')
        fig.save(filename=fname)
        assert os.path.isfile(fname)


def test_save_to_html_with_bad_extension_raises():
    da = scatter()
    fig = Figure(input_node(da),
                 FigConstructor=FigScatter3d,
                 x='x',
                 y='y',
                 z='z',
                 norm='log')
    with pytest.raises(ValueError, match=r'File extension must be \.html'):
        fig.save(filename='plopp_fig3d.png')
