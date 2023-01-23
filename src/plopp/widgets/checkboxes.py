# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from html import escape
from typing import Callable, Dict, List

import ipywidgets as ipw


class Checkboxes(ipw.HBox):
    """
    Widget providing a list of checkboxes, along with a button to toggle them all.

    Parameters
    ----------
    entries:
        List of strings to create the names for the different checkboxes.
    description:
        Global description for all the checkboxes.
    value:
        Default value to set all the checkboxes to.
    """

    def __init__(self, entries: List[str], description: str = "", value: bool = True):
        self.checkboxes = {}
        self._lock = False
        self.description = ipw.Label(value=description)

        for key in entries:
            self.checkboxes[key] = ipw.Checkbox(value=value,
                                                description=f"{escape(key)}",
                                                indent=False,
                                                layout={"width": "initial"})

        to_hbox = [
            self.description,
            ipw.HBox(list(self.checkboxes.values()),
                     layout=ipw.Layout(flex_flow='row wrap'))
        ]

        if len(self.checkboxes) > 1:
            # Add a master button to control all masks in one go
            self.toggle_all_button = ipw.ToggleButton(value=value,
                                                      description="Toggle all",
                                                      disabled=False,
                                                      button_style="",
                                                      layout={"width": "initial"})
            for cbox in self.checkboxes.values():
                ipw.jsdlink((self.toggle_all_button, 'value'), (cbox, 'value'))
            to_hbox.insert(1, self.toggle_all_button)

        super().__init__(to_hbox)

    def _plopp_observe_(self, callback: Callable, **kwargs):
        for chbx in self.checkboxes.values():
            chbx.observe(callback, **kwargs)

    @property
    def value(self) -> Dict[str, bool]:
        """
        Returns a dict containing one entry per checkbox, giving the checkbox's value.
        """
        return {key: chbx.value for key, chbx in self.checkboxes.items()}
