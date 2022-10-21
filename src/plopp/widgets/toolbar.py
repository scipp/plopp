# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ipywidgets import VBox


class Toolbar(VBox):
    '''
    Custom toolbar with additional buttons for controlling log scales and
    normalization, and with back/forward buttons removed.
    '''

    def __init__(self, tools=None):
        self.tools = {}
        if tools is not None:
            for key, tool in tools.items():
                setattr(self, key, tool.callback)
                self.tools[key] = tool

        super().__init__()
        self._update_children()

    def __getitem__(self, key):
        return self.tools[key]

    def __setitem__(self, key, tool):
        self.tools[key] = tool
        self._update_children()

    def __delitem__(self, key):
        del self.tools[key]
        self._update_children()

    def _update_children(self):
        self.children = list(self.tools.values())
