# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

from importlib import util

import matplotlib
import pytest

import plopp as pp

BACKENDS = ['mpl-static', 'mpl-interactive']

BACKENDS_WITH_PLOTLY = BACKENDS.copy()
if util.find_spec('plotly') is not None:
    BACKENDS_WITH_PLOTLY.append('plotly')


def _do_setup(request):
    if request.param == 'mpl-static':
        matplotlib.use('Agg')
        pp.backends['2d'] = 'matplotlib'
    elif request.param == 'mpl-interactive':
        matplotlib.use('module://ipympl.backend_nbagg')
        pp.backends['2d'] = 'matplotlib'
    else:
        pp.backends['2d'] = request.param


@pytest.fixture(params=BACKENDS, autouse=True)
def _setup_backends_mpl(request):
    _do_setup(request)


@pytest.fixture(params=BACKENDS_WITH_PLOTLY, autouse=True)
def _setup_backends_all(request):
    _do_setup(request)
