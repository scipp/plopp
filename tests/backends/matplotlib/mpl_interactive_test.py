# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import pytest

from plopp.data.testing import data_array


@pytest.mark.usefixtures('_use_ipympl')
def test_logx_1d_toolbar_button():
    da = data_array(ndim=1)
    fig = da.plot(scale={'xx': 'log'})
    assert fig.toolbar['logx'].value


@pytest.mark.usefixtures('_use_ipympl')
def test_logy_1d_toolbar_button():
    da = data_array(ndim=1)
    fig = da.plot(norm='log')
    assert fig.toolbar['logy'].value


@pytest.mark.usefixtures('_use_ipympl')
def test_logxy_2d_toolbar_buttons():
    da = data_array(ndim=2)
    fig = da.plot(scale={'xx': 'log', 'yy': 'log'})
    assert fig.toolbar['logx'].value
    assert fig.toolbar['logy'].value


@pytest.mark.usefixtures('_use_ipympl')
def test_log_norm_2d_toolbar_button():
    da = data_array(ndim=2)
    fig = da.plot(norm='log')
    assert fig.toolbar['lognorm'].value
