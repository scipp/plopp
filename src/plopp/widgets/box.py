# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ipywidgets import VBox, HBox, Widget


class Bar:
    """
    A simple mixin to provide add and remove helper methods for HBox/VBox containers.
    """

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
    pass


class HBar(HBox, Bar):
    """
    Horizontal bar container.
    """
    pass


class Box(VBox):
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
        self.widgets = widgets
        children = []
        for view in self.widgets:
            children.append(HBox(view) if isinstance(view, (list, tuple)) else view)
        super().__init__(children)
