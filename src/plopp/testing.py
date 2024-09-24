# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from importlib import util

import matplotlib
import pytest

import plopp as pp

BACKENDS = ['mpl-static', 'mpl-interactive']

BACKENDS_WITH_PLOTLY = BACKENDS.copy()
if util.find_spec('plotly') is not None:
    BACKENDS_WITH_PLOTLY.append('plotly')


def _setup(request):
    group = request.param[0]
    if request.param[1] == 'mpl-static':
        matplotlib.use('Agg')
        pp.backends[group] = 'matplotlib'
    elif request.param[1] == 'mpl-interactive':
        matplotlib.use('module://ipympl.backend_nbagg')
        pp.backends[group] = 'matplotlib'
    else:
        pp.backends[group] = request.param[1]


@pytest.fixture(params=BACKENDS, autouse=True)
def _setup_backends_mpl(request):
    """
    This fixture sets up a parametrization of matplotlib backends for all tests when
    imported.
    """
    _setup(request)


@pytest.fixture(params=BACKENDS_WITH_PLOTLY, autouse=True)
def _setup_backends_all(request):
    """
    This fixture sets up a parametrization of all backends for all tests when imported.
    """
    _setup(request)


@dataclass
class BackendParam:
    param: tuple[str, str]


class Case:
    def __init__(self, backend: tuple[str, str], figure: Callable, data: Callable):
        self.backend = backend
        self.figure = figure
        self.data = data

    def set_backend(self):
        _setup(BackendParam(self.backend))

    def __str__(self) -> str:
        figname = (
            self.figure.func.__name__
            if isinstance(self.figure, partial)
            else self.figure.__name__
        )
        return f'{figname}-{self.backend[1]}'


def to_params(case_list: list[Case]):
    """
    Turn a list of cases into pytest params with a good id for printing.
    """
    return [pytest.param(c, id=str(c)) for c in case_list]
