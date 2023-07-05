# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from plopp import Node
from plopp.backends.matplotlib.interactive import InteractiveFig
from plopp.data.testing import data_array
from plopp.graphics.figimage import FigImage
from plopp.graphics.figline import FigLine


def test_logx_1d_toolbar_button(use_ipympl):
    da = data_array(ndim=1)
    fig = InteractiveFig(Node(da), FigConstructor=FigLine, scale={'xx': 'log'})
    assert fig.toolbar['logx'].value


def test_logy_1d_toolbar_button(use_ipympl):
    da = data_array(ndim=1)
    fig = InteractiveFig(Node(da), FigConstructor=FigLine, norm='log')
    assert fig.toolbar['logy'].value


def test_logxy_2d_toolbar_buttons(use_ipympl):
    da = data_array(ndim=2)
    fig = InteractiveFig(
        Node(da), FigConstructor=FigImage, scale={'xx': 'log', 'yy': 'log'}
    )
    assert fig.toolbar['logx'].value
    assert fig.toolbar['logy'].value


def test_log_norm_2d_toolbar_button(use_ipympl):
    da = data_array(ndim=2)
    fig = InteractiveFig(Node(da), FigConstructor=FigImage, norm='log')
    assert fig.toolbar['lognorm'].value


def test_copy(use_ipympl):
    da = data_array(ndim=1)
    fig = InteractiveFig(Node(da), FigConstructor=FigLine)
    fig2 = fig.copy()
    assert fig.graph_nodes.keys() == fig2.graph_nodes.keys()
    assert fig.artists.keys() == fig2.artists.keys()


def test_copy_keeps_kwargs(use_ipympl):
    da = data_array(ndim=1)
    fig = InteractiveFig(
        Node(da),
        FigConstructor=FigLine,
        scale={'xx': 'log'},
        norm='log',
        grid=True,
        title='A nice title',
    )
    fig2 = fig.copy()
    assert fig2.canvas.xscale == 'log'
    assert fig2.canvas.yscale == 'log'
    assert fig2.canvas.grid
    assert fig2.canvas.title == 'A nice title'
