# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core import View

from abc import abstractmethod
import scipp as sc


class BaseFig(View):
    """
    A View class for figures.
    """

    def __init__(self, *nodes):
        super().__init__(*nodes)
        self.artists = {}
        self.dims = {}

    def notify_view(self, message):
        node_id = message["node_id"]
        new_values = self.graph_nodes[node_id].request_data()
        self.update(new_values=new_values, key=node_id)

    @abstractmethod
    def update(self, new_values: sc.DataArray, key: str, draw: bool):
        return

    def render(self):
        for node in self.graph_nodes.values():
            new_values = node.request_data()
            self.update(new_values=new_values, key=node.id, draw=False)
