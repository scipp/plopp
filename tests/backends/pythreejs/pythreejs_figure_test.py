# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp import input_node, backends
from plopp.data.testing import scatter
from plopp.graphics.figscatter3d import FigScatter3d


def test_log_norm_3d_toolbar_button():
    da = scatter()
    fig = backends.Fig3d(input_node(da),
                         FigConstructor=FigScatter3d,
                         x='x',
                         y='y',
                         z='z',
                         norm='log')
    assert fig.toolbar['lognorm'].value
