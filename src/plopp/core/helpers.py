# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from functools import partial, update_wrapper
from typing import Any, Callable

from .node import Node


def node(func: Callable, *args, **kwargs) -> Callable:
    """
    Create a :class:`Node` from a callable.
    The additional arguments will be parent nodes to the returned node.
    This can also be used as a decorator.

    Parameters
    ----------
    func:
        The callable to create the :class:`Node`.
    """
    partialized = partial(func, *args, **kwargs)
    update_wrapper(partialized, func)

    def make_node(*args, **kwargs):
        return Node(partialized, *args, **kwargs)

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
