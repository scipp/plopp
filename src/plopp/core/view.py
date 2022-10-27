# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from abc import abstractmethod
import uuid


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

    def __init__(self, *nodes):
        self._id = str(uuid.uuid1())
        self.graph_nodes = {}
        for node in nodes:
            node.add_view(self)

    @abstractmethod
    def notify_view(self, _):
        """
        The function that will be called when a parent node is told to notify its
        children and its views.
        This has to be overridden by any child class.
        """
        return

    @property
    def id(self):
        """
        The unique id of the view.
        """
        return self._id
