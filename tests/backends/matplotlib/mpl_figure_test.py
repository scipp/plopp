# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from plopp.backends.matplotlib import MatplotlibBackend
from plopp.backends.matplotlib.interactive import InteractiveFig
from plopp.backends.matplotlib.static import StaticFig
from plopp.graphics.figimage import FigImage
from plopp.graphics.figline import FigLine


def test_create_static_fig1d():
    b = MatplotlibBackend()
    fig = b.figure1d(FigConstructor=FigLine)
    assert isinstance(fig, StaticFig)


def test_create_interactive_fig1d(use_ipympl):
    b = MatplotlibBackend()
    fig = b.figure1d(FigConstructor=FigLine)
    assert isinstance(fig, InteractiveFig)


def test_create_static_fig2d():
    b = MatplotlibBackend()
    fig = b.figure2d(FigConstructor=FigImage)
    assert isinstance(fig, StaticFig)


def test_create_interactive_fig2d(use_ipympl):
    b = MatplotlibBackend()
    fig = b.figure2d(FigConstructor=FigImage)
    assert isinstance(fig, InteractiveFig)
