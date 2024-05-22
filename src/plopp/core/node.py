# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from __future__ import annotations

import uuid
from itertools import chain
from typing import Any

from .view import View


def _no_replace_append(container: list[Node], item: Node, kind: str) -> None:
    """
    Append ``item`` to ``container`` if it is not already in it.
    """
    if item in container:
        tpe = 'View' if kind == 'view' else 'Node'
        raise ValueError(f"{tpe} {item} is already a {kind} in {container}.")
    container.append(item)


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

    def __init__(self, func: Any, *parents: Any, **kwparents: Any) -> None:
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
            val_str = f'={func!r}' if isinstance(func, int | float | str) else ""
            self.name = f'Input <{type(func).__name__}{val_str}>'

        # Attempt to set children after setting name in case error message is needed
        for parent in chain(self.parents, self.kwparents.values()):
            _no_replace_append(parent.children, self, 'child')

    def __call__(self) -> Any:
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

    def remove(self) -> None:
        """
        Remove the node from the graph.
        This attempts to remove clear the list of parents of the node.
        The operation fails is the node has children, as removing it would leave the
        graph in an ill-defined state.
        """
        for child in self.children:
            if self in child.parents:
                child.parents.remove(self)
            child.kwparents = {
                key: parent for key, parent in child.kwparents.items() if parent != self
            }
            child._data = None
        self.children.clear()
        for view in self.views:
            del view.graph_nodes[self.id]
        for parent in chain(self.parents, self.kwparents.values()):
            parent.children.remove(self)
        self.views.clear()
        self.parents.clear()
        self.kwparents.clear()
        self._data = None

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

    def add_parents(self, *parents: Node) -> None:
        """
        Add one or more parents to the node.
        """
        for parent in parents:
            _no_replace_append(self.parents, parent, 'parent')
            _no_replace_append(parent.children, self, 'child')

    def add_kwparents(self, **parents: Node) -> None:
        """
        Add one or more keyword parents to the node.
        """
        for key, parent in parents.items():
            self.kwparents[key] = parent
            _no_replace_append(parent.children, self, 'child')

    def add_view(self, view: View) -> None:
        """
        Add a view to the node.
        """
        _no_replace_append(self.views, view, 'view')
        view.graph_nodes[self.id] = self

    def notify_children(self, message: Any) -> None:
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

    def notify_views(self, message: Any) -> None:
        """
        Notify the node's views with ``message``.

        Parameters
        ----------
        message:
            The message to pass to the views.
        """
        for view in self.views:
            view.notify_view({"node_id": self.id, "message": message})

    def __eq__(self, other: Node | Any) -> bool:
        if not isinstance(other, Node):
            return False
        return self.id == other.id

    def __repr__(self) -> str:
        return f"Node(name={self.name})"

    def __add__(self, other: Node | Any) -> Node:
        return Node(lambda x, y: x + y, self, other)

    def __radd__(self, other: Node | Any) -> Node:
        return Node(lambda x, y: x + y, other, self)

    def __sub__(self, other: Node | Any) -> Node:
        return Node(lambda x, y: x - y, self, other)

    def __rsub__(self, other: Node | Any) -> Node:
        return Node(lambda x, y: x - y, other, self)

    def __mul__(self, other: Node | Any) -> Node:
        return Node(lambda x, y: x * y, self, other)

    def __rmul__(self, other: Node | Any) -> Node:
        return Node(lambda x, y: x * y, other, self)

    def __truediv__(self, other: Node | Any) -> Node:
        return Node(lambda x, y: x / y, self, other)

    def __rtruediv__(self, other: Node | Any) -> Node:
        return Node(lambda x, y: x / y, other, self)
