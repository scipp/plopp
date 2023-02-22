# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from views import SimpleView

from plopp import input_node, node, show_graph


def has_edge(graph, node1, node2):
    """
    Check if graph contains a given edge.
    """
    tail_name = graph._quote_edge(node1)
    head_name = graph._quote_edge(node2)
    return graph._edge(tail=tail_name, head=head_name, attr='') in graph.body


def test_two_nodes_parent_child():
    # [ a ]
    #   |
    # [ b ]
    a = input_node(5)
    b = node(lambda x: x - 2)(a)
    g = show_graph(a)
    assert has_edge(g, a.id, b.id)


def test_two_children():
    #    [ a ]
    #     / \
    #    /   \
    # [ b ] [ c ]
    a = input_node(5)
    b = node(lambda x: x - 2)(a)
    c = node(lambda x: x + 2)(a)
    g = show_graph(a)
    assert has_edge(g, a.id, b.id)
    assert has_edge(g, a.id, c.id)


def test_two_parents():
    # [ a ] [ b ]
    #    \   /
    #     \ /
    #    [ c ]
    a = input_node(5)
    b = input_node(9)
    c = node(lambda x, y: x + y)(a, b)
    g = show_graph(a)
    assert has_edge(g, a.id, c.id)
    assert has_edge(g, b.id, c.id)


def test_two_parents_two_children():
    # [ a ] [ b ]
    #    \   / |
    #     \ /  |
    #    [ c ] |
    #       \  |
    #        \/
    #      [ d ]
    a = input_node(5)
    b = input_node(9)
    c = node(lambda x, y: x + y)(a, b)
    d = node(lambda x, y: x - y)(c, b)
    g = show_graph(a)
    assert has_edge(g, a.id, c.id)
    assert has_edge(g, b.id, c.id)
    assert has_edge(g, c.id, d.id)
    assert has_edge(g, b.id, d.id)


def test_two_grandchildren_have_common_parent():
    #       [ a ]
    #      /     \
    #     /       \
    #    /         \
    # [ b ] [ d ] [ c ]
    #    \   / \   /
    #     \ /   \ /
    #    [ e ] [ f ]
    a = input_node(0)
    b = node(lambda x: x + 1)(a)
    c = node(lambda x: x + 2)(a)
    d = input_node(4)
    e = node(lambda x, y: x + y)(b, d)
    f = node(lambda x, y: x + y)(c, d)
    g = show_graph(a)
    assert has_edge(g, a.id, b.id)
    assert has_edge(g, a.id, c.id)
    assert has_edge(g, b.id, e.id)
    assert has_edge(g, d.id, e.id)
    assert has_edge(g, d.id, f.id)
    assert has_edge(g, c.id, f.id)


def test_graph_with_views():
    #    [ a ]
    #     / \
    #    /   \
    # [ b ] [ View ]
    #   |
    #   |
    # [ View ]
    a = input_node(5)
    b = node(lambda x: x - 2)(x=a)
    av = SimpleView(a)
    bv = SimpleView(b)
    g = show_graph(a)
    assert has_edge(g, a.id, b.id)
    assert has_edge(g, a.id, av.id)
    assert has_edge(g, b.id, bv.id)
