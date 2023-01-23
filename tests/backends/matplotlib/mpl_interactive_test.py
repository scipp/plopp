# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from plopp import input_node
from plopp.backends.matplotlib.interactive import InteractiveFig
from plopp.data.testing import data_array
from plopp.graphics.figimage import FigImage
from plopp.graphics.figline import FigLine


def test_logx_1d_toolbar_button(use_ipympl):
    da = data_array(ndim=1)
    fig = InteractiveFig(input_node(da), FigConstructor=FigLine, scale={'xx': 'log'})
    assert fig.toolbar['logx'].value


def test_logy_1d_toolbar_button(use_ipympl):
    da = data_array(ndim=1)
    fig = InteractiveFig(input_node(da), FigConstructor=FigLine, norm='log')
    assert fig.toolbar['logy'].value


def test_logxy_2d_toolbar_buttons(use_ipympl):
    da = data_array(ndim=2)
    fig = InteractiveFig(input_node(da),
                         FigConstructor=FigImage,
                         scale={
                             'xx': 'log',
                             'yy': 'log'
                         })
    assert fig.toolbar['logx'].value
    assert fig.toolbar['logy'].value


def test_log_norm_2d_toolbar_button(use_ipympl):
    da = data_array(ndim=2)
    fig = InteractiveFig(input_node(da), FigConstructor=FigImage, norm='log')
    assert fig.toolbar['lognorm'].value
