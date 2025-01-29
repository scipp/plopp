# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from html import escape
from itertools import chain

from .node_class import Node
from .view import View


def _make_graphviz_digraph(*args, **kwargs):
    try:
        from graphviz import Digraph
    except ImportError:
        raise RuntimeError(
            "Failed to import `graphviz`. "
            "Use `pip install graphviz` (requires installed `graphviz` executable) or "
            "`conda install -c conda-forge python-graphviz`."
        ) from None
    return Digraph(*args, **kwargs)


def _walk_graph(start, nodes, edges, views, labels):
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
            start=child,
            nodes=nodes,
            edges=edges,
            views=views,
            labels=labels,
        )
    for arg_name, parent in chain(
        ((f'arg_{i}', p) for i, p in enumerate(start.parents)), start.kwparents.items()
    ):
        key = parent.id
        if key not in labels:
            labels[key] = arg_name
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
                labels=labels,
            )

    for view in start.views:
        need_walk = False
        if view.id not in views:
            need_walk = True
        views[view.id] = view.__class__.__name__
        if start.id not in edges:
            edges[start.id] = {view.id}
        else:
            edges[start.id].add(view.id)
        if need_walk:
            for node in view.graph_nodes.values():
                _walk_graph(
                    start=node,
                    nodes=nodes,
                    edges=edges,
                    views=views,
                    labels=labels,
                )


def _make_graph(dot, nodes, edges, labels, views):
    for key, lab in nodes.items():
        dot.node(key, label=lab)
    for key, lab in views.items():
        dot.node(key, label=lab, shape='ellipse', style='filled', color='lightgrey')
    for parent, children in edges.items():
        for child in children:
            dot.edge(
                parent,
                child,
                label=labels.get(parent, '') if child not in views else '',
            )
    return dot


def show_graph(entry: Node | View, **kwargs):
    """
    Display the connected nodes and views as a graph.

    Parameters
    ----------
    entry:
        An entry point in the graph (node or view). This can be any node/view in the
        graph. The graph will be searched from end to end to construct the diagram.
    **kwargs:
        Additional keyword arguments are forwarded to ``graphviz.Digraph``.

    Returns
    -------
    :
        A visual representation of the graph generated with Graphviz.
    """
    dot = _make_graphviz_digraph(strict=True, graph_attr=kwargs)
    dot.attr('node', shape='box', height='0.1')
    nodes = {}
    edges = {}
    views = {}
    labels = {}
    # If input is a View, get the underlying node
    if hasattr(entry, 'graph_nodes'):
        entry = next(iter(entry.graph_nodes.values()))
    _walk_graph(
        start=entry,
        nodes=nodes,
        edges=edges,
        views=views,
        labels=labels,
    )
    return _make_graph(dot=dot, nodes=nodes, edges=edges, labels=labels, views=views)
