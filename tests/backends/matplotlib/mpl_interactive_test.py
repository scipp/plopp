# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp import input_node
from plopp.data.testing import data_array, scatter
from plopp.graphics.figline import FigLine
from plopp.graphics.figimage import FigImage
from plopp.backends.matplotlib.interactive import InteractiveFig1d, InteractiveFig2d


def test_getattr_from_figure(use_ipympl):
    fig1d = InteractiveFig1d(FigConstructor=FigLine)
    assert hasattr(fig1d, 'canvas')
    fig2d = InteractiveFig2d(FigConstructor=FigImage)
    assert hasattr(fig2d, 'colormapper')


def test_logx_1d_toolbar_button(use_ipympl):
    da = data_array(ndim=1)
    fig = InteractiveFig1d(input_node(da), FigConstructor=FigLine, scale={'xx': 'log'})
    assert fig.toolbar['logx'].value


def test_logy_1d_toolbar_button(use_ipympl):
    da = data_array(ndim=1)
    fig = InteractiveFig1d(input_node(da), FigConstructor=FigLine, norm='log')
    assert fig.toolbar['logy'].value


def test_logxy_2d_toolbar_buttons(use_ipympl):
    da = data_array(ndim=2)
    fig = InteractiveFig2d(input_node(da),
                           FigConstructor=FigImage,
                           scale={
                               'xx': 'log',
                               'yy': 'log'
                           })
    assert fig.toolbar['logx'].value
    assert fig.toolbar['logy'].value


def test_log_norm_2d_toolbar_button(use_ipympl):
    da = data_array(ndim=2)
    fig = InteractiveFig2d(input_node(da), FigConstructor=FigImage, norm='log')
    assert fig.toolbar['lognorm'].value
