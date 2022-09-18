# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ipywidgets import VBox, HBox


class Plot(VBox):

    def __init__(self, views):
        self.views = views
        children = []
        for view in self.views:
            children.append(HBox(view) if isinstance(view, (list, tuple)) else view)
        return super().__init__(children)
