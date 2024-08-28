# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

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


@pytest.fixture()
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
