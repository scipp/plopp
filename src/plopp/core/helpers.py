# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from collections.abc import Callable
from typing import Any

from .node_class import Node


def node(func: Callable) -> Callable:
    """
    Create a :class:`Node` from a callable.
    This can also be used as a decorator.

    Parameters
    ----------
    func:
        The callable to create the :class:`Node`.
    """

    def make_node(*args: Any, **kwargs: Any) -> None:
        return Node(func, *args, **kwargs)

    return make_node


def widget_node(widget) -> Node:
    """
    Create a node from a widget. When data is requested from it, it will return the
    ``.value`` attribute of the supplied widget.
    In addition, all of its children will be notified when the ``value`` of the widget
    changes.

    Parameters
    ----------
    widget:
        The widget used to construct the node. This can be a widget from the
        ``ipywidgets`` library, or a custom widget.
    """
    n = Node(func=lambda: widget.value)
    n.name = f'Widget <{type(widget).__name__}: {type(widget.value).__name__}>'
    widget.observe(n.notify_children, names="value")
    return n
