# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.graphics.figline import FigLine
from plopp.graphics.figimage import FigImage
from plopp.backends.matplotlib import Fig1d, Fig2d
from plopp.backends.matplotlib.static import StaticFig
from plopp.backends.matplotlib.interactive import InteractiveFig1d, InteractiveFig2d


def test_create_static_fig1d():
    fig = Fig1d(FigConstructor=FigLine)
    assert isinstance(fig, StaticFig)


def test_create_interactive_fig1d(use_ipympl):
    fig = Fig1d(FigConstructor=FigLine)
    assert isinstance(fig, InteractiveFig1d)


def test_create_static_fig2d():
    fig = Fig2d(FigConstructor=FigImage)
    assert isinstance(fig, StaticFig)


def test_create_interactive_fig2d(use_ipympl):
    fig = Fig2d(FigConstructor=FigImage)
    assert isinstance(fig, InteractiveFig2d)
