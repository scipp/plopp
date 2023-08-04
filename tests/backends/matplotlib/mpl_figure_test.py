# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from plopp.backends.matplotlib import MatplotlibBackend
from plopp.backends.matplotlib.interactive import InteractiveFig
from plopp.backends.matplotlib.static import StaticFig
from plopp.graphics.imageview import ImageView
from plopp.graphics.lineview import LineView


def test_create_static_fig1d():
    b = MatplotlibBackend()
    fig = b.figure1d(View=LineView)
    assert isinstance(fig, StaticFig)


def test_create_interactive_fig1d(use_ipympl):
    b = MatplotlibBackend()
    fig = b.figure1d(View=LineView)
    assert isinstance(fig, InteractiveFig)


def test_create_static_fig2d():
    b = MatplotlibBackend()
    fig = b.figure2d(View=ImageView)
    assert isinstance(fig, StaticFig)


def test_create_interactive_fig2d(use_ipympl):
    b = MatplotlibBackend()
    fig = b.figure2d(View=ImageView)
    assert isinstance(fig, InteractiveFig)
