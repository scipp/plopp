# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from __future__ import annotations

from typing import Dict, Protocol, Tuple

import scipp as sc

from ..core import Node


class CanvasLike(Protocol):
    def autoscale(self) -> None:
        ...

    def draw(self) -> None:
        ...

    def save(self) -> None:
        ...

    @property
    def empty(self) -> bool:
        ...

    @property
    def title(self) -> str:
        ...

    @title.setter
    def title(self, title: str) -> None:
        ...

    @property
    def xlabel(self) -> str:
        ...

    @xlabel.setter
    def xlabel(self, xlabel: str) -> None:
        ...

    @property
    def ylabel(self) -> str:
        ...

    @ylabel.setter
    def ylabel(self, ylabel: str) -> None:
        ...

    @property
    def xscale(self) -> str:
        ...

    @xscale.setter
    def xscale(self, xscale: str) -> None:
        ...

    @property
    def yscale(self) -> str:
        ...

    @yscale.setter
    def yscale(self, yscale: str) -> None:
        ...

    @property
    def xmin(self) -> float:
        ...

    @xmin.setter
    def xmin(self, xmin: float) -> None:
        ...

    @property
    def xmax(self) -> float:
        ...

    @xmax.setter
    def xmax(self, xmax: float) -> None:
        ...

    @property
    def ymin(self) -> float:
        ...

    @ymin.setter
    def ymin(self, ymin: float) -> None:
        ...

    @property
    def ymax(self) -> float:
        ...

    @ymax.setter
    def ymax(self, ymax: float) -> None:
        ...

    @property
    def xrange(self) -> Tuple[float, float]:
        ...

    @xrange.setter
    def xrange(self, xrange: Tuple[float, float]) -> None:
        ...

    @property
    def yrange(self) -> Tuple[float, float]:
        ...

    @yrange.setter
    def yrange(self, yrange: Tuple[float, float]) -> None:
        ...

    def logx(self) -> None:
        ...

    def logy(self) -> None:
        ...


class ArtistLike(Protocol):
    def update(self, new_values: sc.DataArray) -> None:
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

    def save(self, filename: str, **kwargs) -> None:
        ...

    def update(self, *args, **kwargs) -> None:
        ...

    def notify_view(self, *args, **kwargs) -> None:
        ...

    def copy(self, **kwargs) -> FigureLike:
        ...
