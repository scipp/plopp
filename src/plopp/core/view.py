# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)
from __future__ import annotations

import uuid
from abc import abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .node_class import Node


class View:
    """
    A (typically graphical) representation of the data.
    A view must be attached to one or more :class:`Node`.
    Upon receiving a notification from a parent node, it usually requests data from that
    node in order to display it visually.

    Parameters
    ----------
    *nodes:
        The nodes that are attached to the view.
    """

    def __init__(self, *nodes: Node) -> None:
        self._id = uuid.uuid4().hex
        self.graph_nodes = {}
        for node in nodes:
            node.add_view(self)

    @property
    def id(self) -> str:
        """
        The unique id of the view.
        """
        return self._id

    def notify_view(self, message: dict[str, Any]) -> None:
        """
        When a notification is received, request data from the corresponding parent node
        and update the relevant artist.

        Parameters
        ----------
        message:
            The notification message containing the node id it originated from.
        """
        node_id = message["node_id"]
        new_values = self.graph_nodes[node_id].request_data()
        self.update(**{node_id: new_values})

    @abstractmethod
    def update(self, *args: Any, **kwargs: Any) -> None:
        """
        Update function which is called when a notification is received.
        This has to be overridden by any child class.
        """
        ...

    def render(self) -> None:
        """
        At the end of figure creation, this function is called to request data from
        all parent nodes and draw the figure.
        """
        self.update(
            **{node.id: node.request_data() for node in self.graph_nodes.values()}
        )
