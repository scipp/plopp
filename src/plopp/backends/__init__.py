# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Scipp contributors (https://github.com/scipp)

from importlib import import_module
from typing import Any

DEFAULTS = {'2d': 'matplotlib', '3d': 'pythreejs'}


class BackendManager:
    def __init__(self):
        self.reset()

    def get(self, group: str, name: str) -> Any:
        """
        Get a backend object from a group (2d or 3d) and a name
        (e.g. canvas, figure, line, scatter, etc.).

        Parameters
        ----------
        group:
            The group of the backend (2d or 3d).
        name:
            The name of the backend object. The class returned will be
            the one with the same name but capitalized.
        """
        module = import_module(f".{self._backends[group]}.{name}", __package__)
        return getattr(module, name.capitalize())

    def is_interactive(self, group: str) -> bool:
        """
        Check if the current backend is interactive.
        """
        module = import_module(f".{self._backends[group]}", __package__)
        return module.is_interactive()

    def __getitem__(self, key: str) -> str:
        return self._backends[key]

    def __setitem__(self, key: str, value: str):
        self._backends[key] = value

    def reset(self):
        self._backends = DEFAULTS.copy()

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f'BackendManager({self._backends})'


__all__ = ['BackendManager']
