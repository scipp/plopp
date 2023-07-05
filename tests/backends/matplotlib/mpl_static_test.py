# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from plopp import Node
from plopp.backends.matplotlib.static import StaticFig
from plopp.data.testing import data_array
from plopp.graphics.figline import FigLine


def test_copy():
    da = data_array(ndim=1)
    fig = StaticFig(Node(da), FigConstructor=FigLine)
    fig2 = fig.copy()
    assert fig.graph_nodes.keys() == fig2.graph_nodes.keys()
    assert fig.artists.keys() == fig2.artists.keys()


def test_copy_keeps_kwargs():
    da = data_array(ndim=1)
    fig = StaticFig(
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
