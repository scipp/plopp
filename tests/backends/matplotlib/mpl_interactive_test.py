# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from plopp import Node
from plopp.backends.matplotlib.interactive import InteractiveFig
from plopp.data.testing import data_array
from plopp.graphics.imageview import ImageView
from plopp.graphics.lineview import LineView


def test_logx_1d_toolbar_button(use_ipympl):
    da = data_array(ndim=1)
    fig = InteractiveFig(LineView, Node(da), scale={'xx': 'log'})
    assert fig.toolbar['logx'].value


def test_logy_1d_toolbar_button(use_ipympl):
    da = data_array(ndim=1)
    fig = InteractiveFig(LineView, Node(da), norm='log')
    assert fig.toolbar['logy'].value


def test_logxy_2d_toolbar_buttons(use_ipympl):
    da = data_array(ndim=2)
    fig = InteractiveFig(ImageView, Node(da), scale={'xx': 'log', 'yy': 'log'})
    assert fig.toolbar['logx'].value
    assert fig.toolbar['logy'].value


def test_log_norm_2d_toolbar_button(use_ipympl):
    da = data_array(ndim=2)
    fig = InteractiveFig(ImageView, Node(da), norm='log')
    assert fig.toolbar['lognorm'].value
