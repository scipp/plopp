# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from __future__ import annotations

from typing import Dict, Protocol

from ..core import Node


class CanvasLike(Protocol):
    ...


class ArtistLike(Protocol):
    ...


class FigureLike(Protocol):
    @property
    def canvas(self) -> CanvasLike:
        ...

    @property
    def artists(self) -> Dict[str, ArtistLike]:
        ...

    @property
    def graph_nodes(self) -> Dict[str, Node]:
        ...

    @property
    def id(self) -> str:
        ...

    def crop(self, **limits) -> None:
        ...

    def save(self, filename: str, **kwargs) -> None:
        ...

    def update(self, *args, **kwargs) -> None:
        ...

    def notify_view(self, *args, **kwargs) -> None:
        ...

    def copy(self, **kwargs) -> FigureLike:
        ...
