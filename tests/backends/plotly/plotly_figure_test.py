# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import pytest

from plopp import input_node
from plopp.backends.plotly.figure import Figure
from plopp.data.testing import data_array
from plopp.graphics.figline import FigLine

pytest.importorskip("plotly")


def test_logx_1d_toolbar_button():
    da = data_array(ndim=1)
    fig = Figure(input_node(da), FigConstructor=FigLine, scale={'xx': 'log'})
    assert fig.toolbar['logx'].value


def test_logy_1d_toolbar_button():
    da = data_array(ndim=1)
    fig = Figure(input_node(da), FigConstructor=FigLine, norm='log')
    assert fig.toolbar['logy'].value
