# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from html import escape

from .model import Node


def _make_graphviz_digraph(*args, **kwargs):
    try:
        from graphviz import Digraph
    except ImportError:
        raise RuntimeError(
            "Failed to import `graphviz`. "
            "Use `pip install graphviz` (requires installed `graphviz` executable) or "
            "`conda install -c conda-forge python-graphviz`."
        )
    return Digraph(*args, **kwargs)


def _walk_graph(start, nodes, edges, views, hide_views):
    label = (
        escape(str(start.func)) + '\nid = ' + start.id
        if start.name is None
        else escape(start.name)
    )
    nodes[start.id] = label
    for child in start.children:
        if start.id not in edges:
            edges[start.id] = {child.id}
        else:
            edges[start.id].add(child.id)
        _walk_graph(
            start=child, nodes=nodes, edges=edges, views=views, hide_views=hide_views
        )
    for parent in start.parents + list(start.kwparents.values()):
        key = parent.id
        if key not in nodes:
            if key not in edges:
                edges[key] = {start.id}
            else:
                edges[key].add(start.id)
            _walk_graph(
                start=parent,
                nodes=nodes,
                edges=edges,
                views=views,
                hide_views=hide_views,
            )
    if not hide_views:
        for view in start.views:
            views[view.id] = view.__class__.__name__
            if start.id not in edges:
                edges[start.id] = {view.id}
            else:
                edges[start.id].add(view.id)


def _make_graph(dot, nodes, edges, views):
    for key, lab in nodes.items():
        dot.node(key, label=lab)
    for key, lab in views.items():
        dot.node(key, label=lab, shape='ellipse', style='filled', color='lightgrey')
    for parent, children in edges.items():
        for child in children:
            dot.edge(parent, child)
    return dot


def show_graph(node: Node, hide_views: bool = False):
    """
    Display the connected nodes and views as a graph.

    Parameters
    ----------
    node:
        A node which is part of the graph. This can be any node in the graph.
        The graph will be searched from end to end to construct the figure.
    hide_views:
        Do not show the views associated with the nodes if `True`.

    Returns
    -------
    :
        A visual representation of the graph generated with Graphviz.
    """
    dot = _make_graphviz_digraph(strict=True)
    dot.attr('node', shape='box', height='0.1')
    nodes = {}
    edges = {}
    views = {}
    _walk_graph(
        start=node, nodes=nodes, edges=edges, views=views, hide_views=hide_views
    )
    return _make_graph(dot=dot, nodes=nodes, edges=edges, views=views)
