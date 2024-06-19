# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

# DEFAULTS = {'2d': 'matplotlib', '3d': 'pythreejs'}
from typing import Any

from .matplotlib import MplLibrary
from .pythreejs import P3jsLibrary


class LibManager:
    def __init__(self, library):
        self._library = library

    def __getitem__(self, name: str) -> Any:
        return self._library[name]

    def module(self, name: str) -> Any:
        return self._library.module(name)


dispatcher = {"2d": LibManager(MplLibrary()), "3d": LibManager(P3jsLibrary())}
