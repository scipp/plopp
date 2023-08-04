# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from plopp import Node
from plopp.backends.matplotlib.interactive import InteractiveFig
from plopp.backends.matplotlib.static import StaticFig
from plopp.backends.matplotlib.utils import copy_figure
from plopp.data.testing import data_array
from plopp.graphics.lineview import LineView


def do_test_copy(Fig):
    da = data_array(ndim=1)
    original = Fig(LineView, Node(da))
    copy = copy_figure(original)
    assert original.graph_nodes.keys() == copy.graph_nodes.keys()
    assert original.artists.keys() == copy.artists.keys()


def do_test_copy_keeps_kwargs(Fig):
    da = data_array(ndim=1)
    original = Fig(
        LineView,
        Node(da),
        scale={'xx': 'log'},
        norm='log',
        grid=True,
        title='A nice title',
    )
    copy = copy_figure(original)
    assert copy.canvas.xscale == 'log'
    assert copy.canvas.yscale == 'log'
    assert copy.canvas.grid
    assert copy.canvas.title == 'A nice title'


def test_copy_static():
    do_test_copy(StaticFig)


def test_copy_static_keeps_kwargs():
    do_test_copy_keeps_kwargs(StaticFig)


def test_copy_interactive(use_ipympl):
    do_test_copy(InteractiveFig)


def test_copy_interactive_keeps_kwargs(use_ipympl):
    do_test_copy_keeps_kwargs(InteractiveFig)
