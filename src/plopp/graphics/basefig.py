# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from abc import abstractmethod
import uuid


class BaseFig:
    """
    A View class for figures.
    """

    def __init__(self, *nodes):
        self.id = str(uuid.uuid1())
        self.graph_nodes = {}
        for node in nodes:
            node.add_view(self)
        self._children = {}
        self.dims = {}

    def notify_view(self, message):
        node_id = message["node_id"]
        new_values = self.graph_nodes[node_id].request_data()
        self.update(new_values=new_values, key=node_id)

    def get_child(self, key):
        return self._children[key]

    @abstractmethod
    def update(self):
        return

    def render(self):
        for node in self.graph_nodes.values():
            new_values = node.request_data()
            self.update(new_values=new_values, key=node.id, draw=False)
        self.canvas.autoscale()
