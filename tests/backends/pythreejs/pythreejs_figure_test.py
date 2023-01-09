# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp import input_node
from plopp.data.testing import scatter
from plopp.backends.pythreejs.figure import Figure
from plopp.graphics.figscatter3d import FigScatter3d
import tempfile
import os


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
        fname = os.path.join(path, 'plopp_fig.html')
        fig.save(filename=fname)
        assert os.path.isfile(fname)
