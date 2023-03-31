# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from typing import Callable

from .node import Node


def node(func: Callable) -> Callable:
    """
    Create a :class:`Node` from a callable.
    This can also be used as a decorator.

    Parameters
    ----------
    func:
        The callable to create the :class:`Node`.
    """

    def make_node(*args, **kwargs):
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
    # TODO: Our custom widgets have a '_plopp_observe' method instead of 'observe'
    # because inheriting from VBox causes errors when overriding the 'observe' method
    # (see https://bit.ly/3SggPVS).
    observe_func = (
        widget._plopp_observe_ if hasattr(widget, '_plopp_observe_') else widget.observe
    )
    observe_func(n.notify_children, names="value")
    return n
