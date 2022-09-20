# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ipywidgets import VBox, HBox


class Box(VBox):
    """
    Container widget that accepts a list of items. For each item in the list, if the
    item is itself a list, it will be bade into a horizontal row of the underlying
    items, if not, the item will span then entire row.
    Finally, all the rows will be placed inside a vertical box container.
    """

    def __init__(self, widgets):
        self.widgets = widgets
        children = []
        for view in self.widgets:
            children.append(HBox(view) if isinstance(view, (list, tuple)) else view)
        return super().__init__(children)
