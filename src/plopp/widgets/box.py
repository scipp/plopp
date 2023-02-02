# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from ipywidgets import HBox, VBox, Widget


class Bar:
    """
    A simple mixin to provide add and remove helper methods for HBox/VBox containers.
    """

    def __len__(self):
        return len(self.children)

    def add(self, obj: Widget):
        """
        Append a widget to the list of children.
        """
        self.children = list(self.children) + [obj]

    def remove(self, obj: Widget):
        """
        Remove a widget from the list of children.
        """
        children = list(self.children)
        children.remove(obj)
        self.children = children


class VBar(VBox, Bar):
    """
    Vertical bar container.
    """

    def __getitem__(self, ind):
        if isinstance(ind, int):
            return self.children[ind]
        elif isinstance(ind, slice):
            return VBar(self.children[ind])


class HBar(HBox, Bar):
    """
    Horizontal bar container.
    """

    def __getitem__(self, ind):
        if isinstance(ind, int):
            return self.children[ind]
        elif isinstance(ind, slice):
            return HBar(self.children[ind])


class Box(VBar):
    """
    Container widget that accepts a list of items. For each item in the list, if the
    item is itself a list, it will be made into a horizontal row of the underlying
    items, if not, the item will span then entire row.
    Finally, all the rows will be placed inside a vertical box container.

    Parameters
    ----------

    widgets:
        List of widgets to place in the box.
    """

    def __init__(self, widgets):
        children = []
        for view in widgets:
            children.append(HBar(view) if isinstance(view, (list, tuple)) else view)
        super().__init__(children)
