# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import numpy as np
import pytest
import scipp as sc

from plopp.core.limits import find_limits, fix_empty_range


def test_find_limits():
    da = sc.DataArray(data=sc.arange('x', 11.0, unit='m'))
    lims = find_limits(da)
    assert sc.identical(lims[0], sc.scalar(0.0, unit='m'))
    assert sc.identical(lims[1], sc.scalar(10.0, unit='m'))


def test_find_limits_log():
    da = sc.DataArray(data=sc.arange('x', 11.0, unit='m'))
    lims = find_limits(da, scale='log')
    assert sc.identical(lims[0], sc.scalar(1.0, unit='m'))
    assert sc.identical(lims[1], sc.scalar(10.0, unit='m'))


def test_find_limits_log_int():
    da = sc.DataArray(data=sc.arange('x', 11, unit='m'))
    lims = find_limits(da, scale='log')
    assert sc.identical(lims[0], sc.scalar(1, unit='m'))
    assert sc.identical(lims[1], sc.scalar(10, unit='m'))


def test_find_limits_with_nan():
    da = sc.DataArray(data=sc.arange('x', 11.0, unit='m'))
    da.values[5] = np.nan
    lims = find_limits(da)
    assert sc.identical(lims[0], sc.scalar(0.0, unit='m'))
    assert sc.identical(lims[1], sc.scalar(10.0, unit='m'))


def test_find_limits_with_inf():
    da = sc.DataArray(data=sc.arange('x', 11.0, unit='m'))
    da.values[5] = np.inf
    lims = find_limits(da)
    assert sc.identical(lims[0], sc.scalar(0.0, unit='m'))
    assert sc.identical(lims[1], sc.scalar(10.0, unit='m'))


def test_find_limits_with_ninf():
    da = sc.DataArray(data=sc.arange('x', 11.0, unit='m'))
    da.values[5] = -np.inf
    lims = find_limits(da)
    assert sc.identical(lims[0], sc.scalar(0.0, unit='m'))
    assert sc.identical(lims[1], sc.scalar(10.0, unit='m'))


def test_find_limits_no_finite_values_raises():
    da = sc.DataArray(
        data=sc.array(dims=['x'], values=[np.nan, np.inf, -np.inf, np.nan], unit='m')
    )
    with pytest.raises(ValueError, match="No finite values were found in array"):
        _ = find_limits(da)


def test_find_limits_all_zeros():
    da = sc.DataArray(data=sc.zeros(sizes={'x': 5}, unit='s'))
    lims = find_limits(da)
    assert sc.identical(lims[0], sc.scalar(0.0, unit='s'))
    assert sc.identical(lims[1], sc.scalar(0.0, unit='s'))


def test_find_limits_all_zeros_log_uses_default_positive_values():
    da = sc.DataArray(data=sc.zeros(sizes={'x': 5}, unit='s'))
    lims = find_limits(da, scale='log')
    zero = sc.scalar(0.0, unit='s')
    assert lims[0] > zero
    assert lims[1] > zero
    assert lims[0] < lims[1]


def test_find_limits_ignores_masks():
    x = sc.arange('x', 11.0, unit='m')
    da = sc.DataArray(data=x, masks={'mask': x > sc.scalar(5.0, unit='m')})
    lims = find_limits(da)
    assert sc.identical(lims[0], sc.scalar(0.0, unit='m'))
    assert sc.identical(lims[1], sc.scalar(5.0, unit='m'))


def test_find_limits_ignores_masks_log():
    x = sc.arange('x', 11.0, unit='m')
    da = sc.DataArray(data=x, masks={'mask': x < sc.scalar(3.0, unit='m')})
    lims = find_limits(da)
    assert sc.identical(lims[0], sc.scalar(3.0, unit='m'))
    assert sc.identical(lims[1], sc.scalar(10.0, unit='m'))


def test_find_limits_with_padding():
    da = sc.DataArray(data=sc.arange('x', 11.0, unit='m'))
    lims = find_limits(da, pad=True)
    assert lims[0] < sc.scalar(0.0, unit='m')
    assert lims[1] > sc.scalar(10.0, unit='m')


def test_find_limits_with_padding_log():
    da = sc.DataArray(data=sc.arange('x', 11.0, unit='m'))
    lims = find_limits(da, scale='log', pad=True)
    assert lims[0] < sc.scalar(1.0, unit='m')
    assert lims[0] > sc.scalar(0.0, unit='m')
    assert lims[1] > sc.scalar(10.0, unit='m')


def test_find_limits_with_strings():
    da = sc.DataArray(
        data=sc.array(dims=['x'], values=['a', 'b', 'c', 'd', 'e'], unit='K')
    )
    lims = find_limits(da)
    assert sc.identical(lims[0], sc.scalar(0.0, unit='K'))
    assert sc.identical(lims[1], sc.scalar(4.0, unit='K'))


def test_find_limits_datetime():
    time = np.arange(
        np.datetime64('2017-03-16T20:58:17'), np.datetime64('2017-03-16T21:15:17'), 20
    )
    da = sc.DataArray(data=sc.array(dims=['time'], values=time))
    lims = find_limits(da)
    assert sc.identical(lims[0], sc.scalar(time[0], unit='s'))
    assert sc.identical(lims[1], sc.scalar(time[-1], unit='s'))


def test_fix_empty_range():
    a = sc.scalar(5.0, unit='m')
    b = sc.scalar(10.0, unit='m')
    lims = fix_empty_range((a, b))
    assert sc.identical(lims[0], a)
    assert sc.identical(lims[1], b)


def test_fix_empty_range_same_values():
    a = sc.scalar(5.0, unit='m')
    lims = fix_empty_range((a, a))
    assert sc.identical(lims[0], sc.scalar(2.5, unit='m'))
    assert sc.identical(lims[1], sc.scalar(7.5, unit='m'))
    lims = fix_empty_range((-a, -a))
    assert sc.identical(lims[0], sc.scalar(-7.5, unit='m'))
    assert sc.identical(lims[1], sc.scalar(-2.5, unit='m'))


def test_fix_empty_range_zeros_values():
    a = sc.scalar(0.0, unit='m')
    lims = fix_empty_range((a, a))
    assert sc.identical(lims[0], sc.scalar(-0.5, unit='m'))
    assert sc.identical(lims[1], sc.scalar(0.5, unit='m'))
