# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from itertools import chain
from functools import partial
import uuid


class Node:

    def __init__(self, func, *parents, **kwparents):
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
        return self._id

    def remove(self):
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

    def request_data(self):
        if self._data is None:
            args = (parent.request_data() for parent in self.parents)
            kwargs = {
                key: parent.request_data()
                for key, parent in self.kwparents.items()
            }
            self._data = self.func(*args, **kwargs)
        return self._data

    def add_child(self, child):
        self.children.append(child)

    def add_view(self, view):
        self.views.append(view)
        view.graph_nodes[self.id] = self

    def notify_children(self, message):
        self._data = None
        self.notify_views(message)
        for child in self.children:
            child.notify_children(message)

    def notify_views(self, message):
        for view in self.views:
            view.notify_view({"node_id": self.id, "message": message})


def node(func, *args, **kwargs):
    partialized = partial(func, *args, **kwargs)

    def make_node(*args, **kwargs):
        return Node(partialized, *args, **kwargs)

    return make_node


def input_node(obj):
    return Node(lambda: obj)


def widget_node(widget):
    n = Node(func=lambda: widget.value)
    # TODO: Our custom widgets have a '_plopp_observe' method instead of 'observe'
    # because inheriting from VBox causes errors when overriding the 'observe' method
    # (see https://bit.ly/3SggPVS).
    func = widget._plopp_observe_ if hasattr(widget,
                                             '_plopp_observe_') else widget.observe
    func(n.notify_children, names="value")
    return n
