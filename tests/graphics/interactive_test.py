# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

import plopp as pp
from plopp.data.testing import data_array
from plopp.graphics.interactive import (InteractiveFig1d, InteractiveFig2d,
                                        InteractiveFig3d)
import pytest
import scipp as sc
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
    fig = InteractiveFig3d()
    assert hasattr(fig, 'toolbar')
    assert hasattr(fig, 'left_bar')
    assert hasattr(fig, 'right_bar')
    assert hasattr(fig, 'bottom_bar')
    assert hasattr(fig, 'top_bar')


def test_getattr_from_figure(use_ipympl):
    fig = InteractiveFig1d()
    assert hasattr(fig, canvas)
