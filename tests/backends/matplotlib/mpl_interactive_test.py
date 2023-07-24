# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from plopp import Node
from plopp.backends.matplotlib.interactive import InteractiveFig
from plopp.data.testing import data_array
from plopp.graphics.figimage import FigImage
from plopp.graphics.figline import FigLine


def test_logx_1d_toolbar_button(use_ipympl):
    da = data_array(ndim=1)
    fig = InteractiveFig(FigLine, Node(da), scale={'xx': 'log'})
    assert fig.toolbar['logx'].value


def test_logy_1d_toolbar_button(use_ipympl):
    da = data_array(ndim=1)
    fig = InteractiveFig(FigLine, Node(da), norm='log')
    assert fig.toolbar['logy'].value


def test_logxy_2d_toolbar_buttons(use_ipympl):
    da = data_array(ndim=2)
    fig = InteractiveFig(FigImage, Node(da), scale={'xx': 'log', 'yy': 'log'})
    assert fig.toolbar['logx'].value
    assert fig.toolbar['logy'].value


def test_log_norm_2d_toolbar_button(use_ipympl):
    da = data_array(ndim=2)
    fig = InteractiveFig(FigImage, Node(da), norm='log')
    assert fig.toolbar['lognorm'].value
