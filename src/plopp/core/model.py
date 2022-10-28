# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from functools import partial
from itertools import chain
from typing import Callable, Any
import uuid


class Node:
    """
    A node that can have parent and children nodes, to create a graph.
    A node must be constructed from a callable ``func``.

    Parameters
    ----------
    func:
        The callable that is called when data is requested from the node.
    *parents:
        Positional arguments that represent the positional arguments of the function
        ``func``.
    *kwparents:
        Keyword arguments that represent the keyword arguments of the function ``func``.
    """

    def __init__(self, func: Callable, *parents, **kwparents):
        if not callable(func):
            raise ValueError("A node can only be created using a callable func.")
        self.func = func
        self._id = str(uuid.uuid1())
        self.children = []
        self.views = []
        self.parents = list(parents)
        self.kwparents = dict(kwparents)
        for parent in chain(self.parents, self.kwparents.values()):
            parent.add_child(self)
        self._data = None
        self.name = None

    @property
    def id(self):
        """
        The unique uuid of the node. This differs from the ``name`` which can be any
        string.
        """
        return self._id

    def remove(self):
        """
        Remove the node from the graph.
        This attempts to remove clear the list of parents of the node.
        The operation fails is the node has children, as removing it would leave the
        graph in an ill-defined state.
        """
        if self.children:
            raise RuntimeError(
                f"Cannot delete node because it has children {self.children}.")
        for view in self.views:
            del view.graph_nodes[self.id]
        for parent in chain(self.parents, self.kwparents.values()):
            parent.children.remove(self)
        self.views.clear()
        self.parents.clear()
        self.kwparents.clear()

    def request_data(self) -> Any:
        """
        Request data from the node. This in turn requests data from all of the node's
        parents, and passes those results as arguments to the node's own ``func``.
        The result from calling the function is cached, to limit the number of times
        the graph is traversed.
        """
        if self._data is None:
            args = (parent.request_data() for parent in self.parents)
            kwargs = {
                key: parent.request_data()
                for key, parent in self.kwparents.items()
            }
            self._data = self.func(*args, **kwargs)
        return self._data

    def add_child(self, child):
        """
        Add a child to the node.
        """
        self.children.append(child)

    def add_view(self, view):
        """
        Add a view to the node.
        """
        self.views.append(view)
        view.graph_nodes[self.id] = self

    def notify_children(self, message: Any):
        """
        Notify all of the node's children with ``message``.
        Receiving a notification also means that the local copy of the data is
        out-of-date, and it is thus reset.

        Parameters
        ----------
        message:
            The message to pass to the children.
        """
        self._data = None
        self.notify_views(message)
        for child in self.children:
            child.notify_children(message)

    def notify_views(self, message: Any):
        """
        Notify the node's views with ``message``.

        Parameters
        ----------
        message:
            The message to pass to the views.
        """
        for view in self.views:
            view.notify_view({"node_id": self.id, "message": message})


def node(func: Callable, *args, **kwargs) -> Callable:
    """
    Create a ``Node`` from a callable. The additional arguments will be parent nodes to
    the returned node.
    This can also be used as a decorator.

    Parameters
    ----------
    func:
        The callable to create the ``Node``.
    """
    partialized = partial(func, *args, **kwargs)

    def make_node(*args, **kwargs):
        return Node(partialized, *args, **kwargs)

    return make_node


def input_node(obj: Any):
    """
    Create a simple node that returns the supplied object when data is requested from
    it. This node has no parents, and typically lives at the top of a graph to provide
    the raw input data.

    Parameters
    ----------
    obj:
        The object to return when data is requested from the node.
    """
    return Node(lambda: obj)


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
    # TODO: Our custom widgets have a '_plopp_observe' method instead of 'observe'
    # because inheriting from VBox causes errors when overriding the 'observe' method
    # (see https://bit.ly/3SggPVS).
    func = widget._plopp_observe_ if hasattr(widget,
                                             '_plopp_observe_') else widget.observe
    func(n.notify_children, names="value")
    return n
