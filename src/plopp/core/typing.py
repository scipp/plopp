# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from typing import Dict, Union

from numpy import ndarray

from scipp.typing import VariableLike

from .node import Node


class VisibleDeprecationWarning(UserWarning):
    """Visible deprecation warning.

    By default, Python and in particular Jupyter will not show deprecation
    warnings, so this class can be used when a very visible warning is helpful.
    """


VisibleDeprecationWarning.__module__ = 'plopp'

Plottable = Union[VariableLike, ndarray, Dict[str, Union[VariableLike, ndarray]], Node]
