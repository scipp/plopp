# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from importlib import util

import matplotlib
import matplotlib.pyplot as plt
import pytest

import plopp as pp


@pytest.fixture(autouse=True)
def _reset_mpl_defaults():
    matplotlib.rcdefaults()
    matplotlib.use('Agg')
    pp.backends.reset()


@pytest.fixture(autouse=True)
def _close_figures():
    """
    Force closing all figures after each test case.
    Otherwise, the figures consume a lot of memory and matplotlib complains.
    """
    yield
    for fig in map(plt.figure, plt.get_fignums()):
        plt.close(fig)


@pytest.fixture
def _use_ipympl():
    matplotlib.use('module://ipympl.backend_nbagg')


def pytest_sessionfinish(session, exitstatus):
    """
    When running no tests (e.g. in the noplotly tox env), pytest returns the exit code
    5, which causes the tox to fail. We use this to catch the exit status and convert
    it to 0.
    See https://github.com/pytest-dev/pytest/issues/2393#issuecomment-452634365
    """
    if exitstatus == 5:
        session.exitstatus = 0


BACKENDS_MPL = [('2d', 'mpl-static'), ('2d', 'mpl-interactive')]
BACKENDS_MPL_INTERACTIVE = [('2d', 'mpl-interactive')]
BACKENDS_PLOTLY = [('2d', 'plotly')] if util.find_spec('plotly') is not None else []


def _select_backend(backend):
    group = backend[0]
    if backend[1] == 'mpl-static':
        matplotlib.use('Agg')
        pp.backends[group] = 'matplotlib'
    elif backend[1] == 'mpl-interactive':
        matplotlib.use('module://ipympl.backend_nbagg')
        pp.backends[group] = 'matplotlib'
    else:
        pp.backends[group] = backend[1]


def _make_fixture_args(params: list):
    return {"params": params, "ids": [x[1] for x in params]}


@pytest.fixture
def set_backend(backend):
    _select_backend(backend)


@pytest.fixture(**_make_fixture_args(BACKENDS_MPL))
def _parametrize_mpl_backends(request):
    _select_backend(request.param)


@pytest.fixture(**_make_fixture_args(BACKENDS_MPL + BACKENDS_PLOTLY))
def _parametrize_all_backends(request):
    _select_backend(request.param)


@pytest.fixture(**_make_fixture_args(BACKENDS_MPL_INTERACTIVE + BACKENDS_PLOTLY))
def _parametrize_interactive_1d_backends(request):
    _select_backend(request.param)


@pytest.fixture(**_make_fixture_args(BACKENDS_MPL_INTERACTIVE))
def _parametrize_interactive_2d_backends(request):
    _select_backend(request.param)
