# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ipywidgets import VBox
from typing import Any, Dict


class Toolbar(VBox):
    """
    Custom toolbar to control interactive figures.

    Parameters
    ----------
    tools:
        Dictionary of tools to populate the toolbar.
    """

    def __init__(self, tools: Dict[str, Any] = None):
        self.tools = {}
        if tools is not None:
            for key, tool in tools.items():
                setattr(self, key, tool.callback)
                self.tools[key] = tool

        super().__init__()
        self._update_children()

    def __getitem__(self, key: str) -> Any:
        return self.tools[key]

    def __setitem__(self, key: str, tool: Any):
        self.tools[key] = tool
        self._update_children()

    def __delitem__(self, key: str):
        del self.tools[key]
        self._update_children()

    def _update_children(self):
        self.children = list(self.tools.values())
