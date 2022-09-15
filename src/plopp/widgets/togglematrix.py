# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..displayable import Displayable
import ipywidgets as ipw


class ToggleButtonRow(Displayable):

    def __init__(self, dims, value, index, callback):
        self._dims = dims
        self._buttons = {
            dim: ipw.Button(description=dim,
                            button_style='info' if dim == value else '',
                            layout={'width': 'initial'})
            for dim in dims
        }

        for dim, b in self._buttons.items():
            b.on_click(callback)
            setattr(b, 'index', index)
            setattr(b, 'dim', dim)

    @property
    def value(self):
        for dim, b in self._buttons.items():
            if b.button_style == 'info':
                return dim

    @value.setter
    def value(self, dim):
        for b in self._buttons.values():
            b.button_style = 'info' if b.dim == dim else ''

    def to_widget(self) -> ipw.Widget:
        return ipw.HBox(list(self._buttons.values()))


class ToggleButtonMatrix(Displayable):

    def __init__(self, dims, selected):
        self._dims = dims
        self._selected = selected
        self._button_rows = {
            ind: ToggleButtonRow(dims=self._dims,
                                 value=sel,
                                 index=ind,
                                 callback=self._sync_buttons)
            for ind, sel in enumerate(self._selected)
        }

    def __getitem__(self, ind):
        return self._button_rows[ind]

    def to_widget(self) -> ipw.Widget:
        return ipw.VBox([row.to_widget() for row in self._button_rows.values()])

    def _sync_buttons(self, owner):
        if owner.button_style == 'info':
            return
        old_dim = self._button_rows[owner.index].value
        # Toggle buttons in other rows
        for ind in set(self._button_rows.keys()) - {owner.index}:
            if self._button_rows[ind].value == owner.dim:
                self._button_rows[ind].value = old_dim
        self._button_rows[owner.index].value = owner.dim

    def on_click(self, callback):
        for row in self._button_rows.values():
            for b in row.values():
                b.on_click(callback)
