# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)
import pytest
import scipp as sc

import plopp as pp


def test_line_creation(use_ipympl):
    da = pp.data.data3d()
    ip = pp.inspector(da)
    fig2d = ip[0][0]
    fig1d = ip[0][1]
    # Activate the inspector tool
    fig2d.toolbar['inspect'].value = True
    assert not fig1d.canvas.dims
    assert len(fig1d.artists) == 0
    fig2d.toolbar['inspect']._tool.click(10, 10)
    assert fig1d.canvas.dims == {'x': da.dims[-1]}
    assert len(fig1d.artists) == 1
    fig2d.toolbar['inspect']._tool.click(20, 15)
    assert len(fig1d.artists) == 2


def test_line_removal(use_ipympl):
    da = pp.data.data3d()
    ip = pp.inspector(da)
    fig2d = ip[0][0]
    fig1d = ip[0][1]
    fig2d.toolbar['inspect'].value = True
    assert not fig1d.canvas.dims
    assert len(fig1d.artists) == 0
    fig2d.toolbar['inspect']._tool.click(10, 10)
    assert fig1d.canvas.dims == {'x': da.dims[-1]}
    assert len(fig1d.artists) == 1
    fig2d.toolbar['inspect']._tool.click(20, 15)
    assert len(fig1d.artists) == 2
    fig2d.toolbar['inspect']._tool.remove(1)
    assert len(fig1d.artists) == 1
    fig2d.toolbar['inspect']._tool.remove(0)
    assert len(fig1d.artists) == 0


def test_operation(use_ipympl):
    da = pp.data.data3d()
    ip_sum = pp.inspector(da, operation='sum')
    ip_mean = pp.inspector(da, operation='mean')
    assert ip_sum[0][0]._view.colormapper.vmax > ip_mean[0][0]._view.colormapper.vmax
    assert ip_sum[0][0]._view.colormapper.vmin < ip_mean[0][0]._view.colormapper.vmin


def test_raises_ValueError_when_given_binned_data(use_ipympl):
    da = sc.data.table_xyz(100).bin(x=10, y=20, z=30)
    with pytest.raises(ValueError, match='Cannot plot binned data'):
        pp.inspector(da, orientation='vertical')
