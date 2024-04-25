# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import pytest

import plopp as pp


@pytest.fixture(autouse=True, scope='module')
def _use_plotly():
    pp.backends['2d'] = 'plotly'
    yield
    pp.backends.reset()
