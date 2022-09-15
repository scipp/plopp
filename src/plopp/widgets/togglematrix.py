# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..displayable import Displayable
import ipywidgets as ipw


class ToggleButtonMatrix(Displayable):

    def __init__(self, dims, selected):
        self._dims = dims
        self._selected = selected
        self._buttons = {
            ind: {
                dim: ipw.Button(description=dim,
                                button_style='info' if dim == sel else '',
                                layout={'width': 'initial'})
                for dim in dims
            }
            for ind, sel in enumerate(self._selected)
        }
        for ind, row in self._buttons.items():
            for dim, b in row.items():
                b.on_click(self._sync_buttons)
                setattr(b, 'index', ind)
                setattr(b, 'dim', dim)

    def to_widget(self) -> ipw.Widget:
        return ipw.VBox([
            ipw.HBox([self._buttons[ind][dim] for dim in self._buttons[ind]])
            for ind in self._buttons
        ])

    def _sync_buttons(self, owner):
        if owner.button_style == 'info':
            return
        # Find old value
        for dim, b in self._buttons[owner.index].items():
            if b.button_style == 'info':
                old_dim = dim
                b.button_style = ''
                break
        # Toggle buttons in other rows
        for ind in set(self._buttons.keys()) - {owner.index}:
            for dim, b in self._buttons[ind].items():
                if (dim == owner.dim) and (b.button_style == 'info'):
                    b.button_style = ''
                    self._buttons[ind][old_dim].button_style = 'info'
                    break
        owner.button_style = 'info'
