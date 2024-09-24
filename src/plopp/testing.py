# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from importlib import util

import matplotlib
import pytest

import plopp as pp

BACKENDS_MPL = [('2d', 'mpl-static'), ('2d', 'mpl-interactive')]
BACKENDS_MPL_INTERACTIVE = [('2d', 'mpl-interactive')]

BACKENDS_PLOTLY = [('2d', 'plotly')] if util.find_spec('plotly') is not None else []
# BACKENDS_INTERACTIVE_1D.extend(BACKENDS_PLOTLY)

#     BACKENDS_PLOTLY = ['plotly']
#     BACKENDS_INTERACTIVE_1D = ['mpl-interactive', 'plotly']
# else:
#     BACKENDS_PLOTLY = []
#     BACKENDS_INTERACTIVE_1D = ['mpl-interactive']


def _setup(request):
    group = request.param[0]
    print(f'Using backend {request.param[1]}')
    if request.param[1] == 'mpl-static':
        matplotlib.use('Agg')
        pp.backends[group] = 'matplotlib'
    elif request.param[1] == 'mpl-interactive':
        matplotlib.use('module://ipympl.backend_nbagg')
        pp.backends[group] = 'matplotlib'
    else:
        pp.backends[group] = request.param[1]


@pytest.fixture(params=BACKENDS_MPL, autouse=True)
def _parametrize_mpl_backends(request):
    """
    This fixture sets up a parametrization of matplotlib backends for all tests when
    imported.
    """
    _setup(request)


# @pytest.fixture(params=BACKENDS_MPL_INTERACTIVE, autouse=True)
# def _parametrize_mpl_interactive_backends(request):
#     """
#     This fixture sets up a parametrization of matplotlib interactive backend for all
#     tests when imported.
#     """
#     _setup(request)


@pytest.fixture(params=BACKENDS_MPL + BACKENDS_PLOTLY, autouse=True)
def _parametrize_all_backends(request):
    """
    This fixture sets up a parametrization of all backends for all tests when imported.
    """
    _setup(request)


@pytest.fixture(params=BACKENDS_MPL_INTERACTIVE + BACKENDS_PLOTLY, autouse=True)
def _parametrize_interactive_1d_backends(request):
    """
    This fixture sets up a parametrization of 1d interactive backends for all tests when
    imported.
    """
    _setup(request)


@pytest.fixture(params=BACKENDS_MPL_INTERACTIVE, autouse=True)
def _parametrize_interactive_2d_backends(request):
    """
    This fixture sets up a parametrization of 2d interactive backends for all tests when
    imported.
    """
    _setup(request)


@dataclass
class BackendParam:
    param: tuple[str, str]


class Case:
    def __init__(
        self,
        backend: tuple[str, str] | None = None,
        figure: Callable | None = None,
        data: Callable | None = None,
    ):
        self.backend = backend
        self.figure = figure
        self.data = data

    def set_backend(self):
        _setup(BackendParam(self.backend))

    def __str__(self) -> str:
        out = str(self.backend[1])
        if self.figure is not None:
            figname = (
                self.figure.func.__name__
                if isinstance(self.figure, partial)
                else self.figure.__name__
            )
            out = f'{figname}-{out}'
        return out


def to_params(case_list: list[Case]):
    """
    Turn a list of cases into pytest params with a good id for printing.
    """
    return [pytest.param(c, id=str(c)) for c in case_list]


__all__ = [
    'Case',
    'to_params',
    '_parametrize_mpl_backends',
    '_parametrize_all_backends',
]
