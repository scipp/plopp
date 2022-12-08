# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

import plopp as pp
from plopp.data.testing import data_array, scatter_data
from plopp.graphics.interactive import (InteractiveFig1d, InteractiveFig2d,
                                        InteractiveFig3d)
import pytest
import matplotlib as mpl


@pytest.fixture
def use_ipympl():
    mpl.use('module://ipympl.backend_nbagg')


def test_create_fig1d(use_ipympl):
    fig = InteractiveFig1d()
    assert hasattr(fig, 'toolbar')
    assert hasattr(fig, 'left_bar')
    assert hasattr(fig, 'right_bar')
    assert hasattr(fig, 'bottom_bar')
    assert hasattr(fig, 'top_bar')


def test_create_fig2d(use_ipympl):
    fig = InteractiveFig2d()
    assert hasattr(fig, 'toolbar')
    assert hasattr(fig, 'left_bar')
    assert hasattr(fig, 'right_bar')
    assert hasattr(fig, 'bottom_bar')
    assert hasattr(fig, 'top_bar')


def test_create_fig3d():
    fig = InteractiveFig3d(x='x', y='y', z='z')
    assert hasattr(fig, 'toolbar')
    assert hasattr(fig, 'left_bar')
    assert hasattr(fig, 'right_bar')
    assert hasattr(fig, 'bottom_bar')
    assert hasattr(fig, 'top_bar')


def test_getattr_from_figure(use_ipympl):
    fig1d = InteractiveFig1d()
    assert hasattr(fig1d, 'canvas')
    fig2d = InteractiveFig2d()
    assert hasattr(fig2d, 'colormapper')


def test_logx_1d_toolbar_button(use_ipympl):
    da = data_array(ndim=1)
    fig = InteractiveFig1d(pp.input_node(da), scale={'xx': 'log'})
    assert fig.toolbar['logx'].value


def test_logy_1d_toolbar_button(use_ipympl):
    da = data_array(ndim=1)
    fig = InteractiveFig1d(pp.input_node(da), norm='log')
    assert fig.toolbar['logy'].value


def test_logxy_2d_toolbar_buttons(use_ipympl):
    da = data_array(ndim=2)
    fig = InteractiveFig2d(pp.input_node(da), scale={'xx': 'log', 'yy': 'log'})
    assert fig.toolbar['logx'].value
    assert fig.toolbar['logy'].value


def test_log_norm_2d_toolbar_button(use_ipympl):
    da = data_array(ndim=2)
    fig = InteractiveFig2d(pp.input_node(da), norm='log')
    assert fig.toolbar['lognorm'].value


def test_log_norm_3d_toolbar_button():
    da = scatter_data()
    fig = InteractiveFig3d(pp.input_node(da), x='x', y='y', z='z', norm='log')
    assert fig.toolbar['lognorm'].value
