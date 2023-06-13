# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import plopp as pp
import pytest


@pytest.fixture(autouse=True, scope='module')
def use_plotly():
    pp.backends['2d'] = 'plotly'
    yield
    pp.backends['2d'] = 'matplotlib'
