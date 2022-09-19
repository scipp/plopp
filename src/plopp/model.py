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
        self.id = str(uuid.uuid1())
        self.children = []
        self.views = []
        self.parents = list(parents)
        self.kwparents = dict(kwparents)
        for parent in chain(self.parents, self.kwparents.values()):
            parent.add_child(self)

    def request_data(self):
        args = (parent.request_data() for parent in self.parents)
        kwargs = {key: parent.request_data() for key, parent in self.kwparents.items()}
        return self.func(*args, **kwargs)

    def add_child(self, child):
        self.children.append(child)

    def add_view(self, view):
        self.views.append(view)

    def notify_children(self, message):
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
    # TODO: Our custom widgets have a 'watch' method instead of 'observe' because
    # inheriting from VBox causes errors when overriding the 'observe' method
    # (see https://bit.ly/3SggPVS).
    # We need to be careful that widgets don't get a method named 'watch' in the future.
    func = widget.watch if hasattr(widget, 'watch') else widget.observe
    func(n.notify_children, names="value")
    return n
