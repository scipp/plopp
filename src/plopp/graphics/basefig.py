# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core import View

from abc import abstractmethod
import scipp as sc
from typing import Any, Dict


class BaseFig(View):
    """
    A :class:`View` for figures.

    Parameters
    ----------
    *nodes:
        The nodes that are attached to the view.
    """

    def __init__(self, *nodes):
        super().__init__(*nodes)
        self.artists = {}
        self.dims = {}

    def notify_view(self, message: Dict[str, Any]):
        """
        When a notification is received, request data from the corresponding parent node
        and update the relevant artist.

        Parameters
        ----------
        *message:
            The notification message containing the node id it originated from.
        """
        node_id = message["node_id"]
        new_values = self.graph_nodes[node_id].request_data()
        self.update(new_values=new_values, key=node_id, draw=True)

    @abstractmethod
    def update(self, new_values: sc.DataArray, key: str, draw: bool):
        """
        Update function which is called when a notification is received.
        This has to be overridden by any child class.
        """
        return

    def render(self):
        """
        At the end of figure creation, this function is called to request data from
        all parent nodes and draw the figure.
        """
        for node in self.graph_nodes.values():
            new_values = node.request_data()
            self.update(new_values=new_values, key=node.id, draw=False)
