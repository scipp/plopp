# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp import input_node
from plopp.data.testing import data_array
from plopp.graphics.figline import FigLine
from plopp.backends.plotly import Fig1d


def test_logx_1d_toolbar_button():
    da = data_array(ndim=1)
    fig = Fig1d(input_node(da), FigConstructor=FigLine, scale={'xx': 'log'})
    assert fig.toolbar['logx'].value


def test_logy_1d_toolbar_button():
    da = data_array(ndim=1)
    fig = Fig1d(input_node(da), FigConstructor=FigLine, norm='log')
    assert fig.toolbar['logy'].value
