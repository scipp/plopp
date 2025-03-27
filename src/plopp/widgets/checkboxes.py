# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from html import escape

import ipywidgets as ipw


class Checkboxes(ipw.HBox, ipw.ValueWidget):
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
    toggle_all_button:
        Whether to add a button to toggle all checkboxes at once.
    """

    def __init__(
        self,
        entries: list[str],
        description: str = "",
        value: bool = True,
        toggle_all_button: bool = True,
    ):
        self.checkboxes = {}
        self._lock = False
        self.description = ipw.Label(value=description)

        for key in entries:
            chbx = ipw.Checkbox(
                value=value,
                description=f"{escape(key)}",
                indent=False,
                layout={"width": "initial"},
            )
            chbx.observe(self._on_subwidget_change, names="value")
            self.checkboxes[key] = chbx

        to_hbox = [
            self.description,
            ipw.HBox(
                list(self.checkboxes.values()), layout=ipw.Layout(flex_flow='row wrap')
            ),
        ]

        if len(self.checkboxes) > 1 and toggle_all_button:
            # Add a master button to control all checkboxes in one go
            self.toggle_all_button = ipw.ToggleButton(
                value=value, description="Toggle all", layout={"width": "initial"}
            )
            self.toggle_all_button.observe(self._toggle_all, names="value")
            to_hbox.insert(1, self.toggle_all_button)

        self._on_subwidget_change()
        super().__init__(to_hbox)

    def _toggle_all(self, change: dict):
        self._lock = True
        for chbx in self.checkboxes.values():
            chbx.value = change["new"]
        self._lock = False
        self._on_subwidget_change()

    def _on_subwidget_change(self, _=None):
        """
        The value is a dict containing one entry per checkbox, giving the
        checkbox's value.
        """
        if self._lock:
            return
        self.value = {key: chbx.value for key, chbx in self.checkboxes.items()}
