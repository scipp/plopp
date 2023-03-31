# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from __future__ import annotations

import uuid
import warnings
from itertools import chain
from typing import Any, Union

from .system import VisibleDeprecationWarning
from .view import View


# TODO: Remove this in v23.05.0
def input_node(obj: Any) -> Node:
    """
    Create a simple node that returns the supplied object when data is requested from
    it. This node has no parents, and typically lives at the top of a graph to provide
    the raw input data.

    .. deprecated:: v23.04.0
       Use :class:`Node` instead.

    Parameters
    ----------
    obj:
        The object to return when data is requested from the node.
    """
    warnings.warn(
        "plopp.input_node has been deprecated "
        "and will be removed in Plopp v23.05.0. "
        "Use plopp.Node instead.",
        VisibleDeprecationWarning,
    )
    n = Node(lambda: obj)
    n.name = f'Input <{type(obj).__name__}>'
    return n


class Node:
    """
    A node that can have parent and children nodes, to create a graph.
    A node can be constructed from a callable ``func``, or a raw object. In the case
    of a raw object, a node wrapping the object will be created.

    Parameters
    ----------
    func:
        The callable that is called when data is requested from the node. This can also
        be a raw object, in which case this becomes a callable that returns the object.
    *parents:
        Positional arguments that represent the positional arguments of the function
        ``func``.
    *kwparents:
        Keyword arguments that represent the keyword arguments of the function ``func``.
    """

    def __init__(self, func: Any, *parents, **kwparents):
        func_is_callable = callable(func)
        self._input_value = None
        if func_is_callable:
            self.func = func
        else:
            self._input_value = func
            self.func = lambda: func
        self._id = uuid.uuid4().hex
        self.children = []
        self.views = []
        self.parents = [p if isinstance(p, Node) else Node(p) for p in parents]
        self.kwparents = {
            key: p if isinstance(p, Node) else Node(p) for key, p in kwparents.items()
        }
        for parent in chain(self.parents, self.kwparents.values()):
            parent.add_child(self)
        self._data = None

        if func_is_callable:
            # Set automatic name from function name and arguments
            args_string = ', '.join(
                chain(
                    (f'arg_{i}' for i in range(len(self.parents))),
                    self.kwparents.keys(),
                )
            )
            fname = getattr(self.func, "__name__", str(self.func))
            self.name = f'{fname}({args_string})'
        else:
            val_str = f'={repr(func)}' if isinstance(func, (int, float, str)) else ""
            self.name = f'Input <{type(func).__name__}{val_str}>'

    def __call__(self):
        return self.request_data()

    @property
    def id(self) -> str:
        """
        The unique uuid of the node. This differs from the ``name`` which can be any
        string.
        """
        return self._id

    @property
    def input_value(self) -> Any:
        """
        The input value of the node, if it is an input node.
        """
        return self._input_value

    @property
    def is_input_node(self) -> bool:
        """
        Whether the node is an input node.
        """
        return self._input_value is not None

    def remove(self):
        """
        Remove the node from the graph.
        This attempts to remove clear the list of parents of the node.
        The operation fails is the node has children, as removing it would leave the
        graph in an ill-defined state.
        """
        if self.children:
            raise RuntimeError(
                f"Cannot delete node because it has children {self.children}."
            )
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
                key: parent.request_data() for key, parent in self.kwparents.items()
            }
            self._data = self.func(*args, **kwargs)
        return self._data

    def add_child(self, child: Node):
        """
        Add a child to the node.
        """
        self.children.append(child)

    def add_view(self, view: View):
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

    def __repr__(self) -> str:
        return f"Node(name={self.name})"

    def __add__(self, other: Union[Node, Any]) -> Node:
        return Node(lambda x, y: x + y, self, other)

    def __radd__(self, other: Union[Node, Any]) -> Node:
        return Node(lambda x, y: x + y, other, self)

    def __sub__(self, other: Union[Node, Any]) -> Node:
        return Node(lambda x, y: x - y, self, other)

    def __rsub__(self, other: Union[Node, Any]) -> Node:
        return Node(lambda x, y: x - y, other, self)

    def __mul__(self, other: Union[Node, Any]) -> Node:
        return Node(lambda x, y: x * y, self, other)

    def __rmul__(self, other: Union[Node, Any]) -> Node:
        return Node(lambda x, y: x * y, other, self)

    def __truediv__(self, other: Union[Node, Any]) -> Node:
        return Node(lambda x, y: x / y, self, other)

    def __rtruediv__(self, other: Union[Node, Any]) -> Node:
        return Node(lambda x, y: x / y, other, self)
