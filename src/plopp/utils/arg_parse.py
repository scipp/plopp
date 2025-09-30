# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Scipp contributors (https://github.com/scipp)

from typing import Literal

import scipp as sc


def parse_vmin_vmax_norm(
    vmin: sc.Variable | float | None,
    vmax: sc.Variable | float | None,
    norm: Literal['linear', 'log', None],
    ymin: sc.Variable | float | None,
    ymax: sc.Variable | float | None,
    log: bool,
    y_or_c: str,
) -> tuple[sc.Variable | float | None, sc.Variable | float | None, bool]:
    if vmin is not None:
        if ymin is not None:
            raise ValueError(f'Cannot specify both "vmin" (legacy) and "{y_or_c}min".')
        ymin = vmin
    if vmax is not None:
        if ymax is not None:
            raise ValueError(f'Cannot specify both "vmax" (legacy) and "{y_or_c}max".')
        ymax = vmax
    if norm is not None:
        if log:
            raise ValueError(f'Cannot specify both "norm" (legacy) and "log{y_or_c}".')
        log = norm == 'log'

    return ymin, ymax, log
