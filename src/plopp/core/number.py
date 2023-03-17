# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from typing import Union

import scipp as sc


class Number:

    def __init__(self, value: Union[sc.Variable, int, float]):
        self._value = value

    def __repr__(self):
        return f"Number({self._value})"

    def to(self, unit: str):
        if isinstance(self._value, sc.Variable):
            return self._value.to(unit=unit)
        else:
            return sc.scalar(self._value, unit=unit)
