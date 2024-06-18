# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

# DEFAULTS = {'2d': 'matplotlib', '3d': 'pythreejs'}
from typing import Any

from .matplotlib import Library as MplLibrary


class Dispatcher:
    def __init__(self):
        self._backends = [MplLibrary()]

    def __getitem__(self, name: str) -> Any:
        return self._backends[0][name]

    def module(self, name: str) -> Any:
        return self._backends[0].module(name)
