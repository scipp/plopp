# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import numpy as np
import pytest
import scipp as sc

from plopp.core.limits import find_limits, fix_empty_range


def test_find_limits():
    x = sc.arange('x', 11.0, unit='m')
    lims = find_limits(x)
    assert sc.identical(lims[0], sc.scalar(-0.5, unit='m'))
    assert sc.identical(lims[1], sc.scalar(10.5, unit='m'))


def test_find_limits_log():
    x = sc.arange('x', 11.0, unit='m')
    lims = find_limits(x, scale='log')
    assert sc.identical(lims[0], sc.scalar(10**-0.05, unit='m'))
    assert sc.identical(lims[1], sc.scalar(10**0.05, unit='m'))


def test_find_limits_log_int():
    x = sc.arange('x', 11, unit='m')
    lims = find_limits(x, scale='log')
    assert sc.identical(lims[0], sc.scalar(10**-0.05, unit='m'))
    assert sc.identical(lims[1], sc.scalar(10**0.05, unit='m'))


def test_find_limits_with_nan():
    x = sc.arange('x', 11.0, unit='m')
    x.values[5] = np.nan
    lims = find_limits(x)
    assert sc.identical(lims[0], sc.scalar(-0.5, unit='m'))
    assert sc.identical(lims[1], sc.scalar(10.5, unit='m'))


def test_find_limits_with_inf():
    x = sc.arange('x', 11.0, unit='m')
    x.values[5] = np.inf
    lims = find_limits(x)
    assert sc.identical(lims[0], sc.scalar(-0.5, unit='m'))
    assert sc.identical(lims[1], sc.scalar(10.5, unit='m'))


def test_find_limits_with_ninf():
    x = sc.arange('x', 11.0, unit='m')
    x.values[5] = np.NINF
    lims = find_limits(x)
    assert sc.identical(lims[0], sc.scalar(-0.5, unit='m'))
    assert sc.identical(lims[1], sc.scalar(10.5, unit='m'))


def test_find_limits_no_finite_values_raises():
    x = sc.array(dims=['x'], values=[np.nan, np.inf, np.NINF, np.nan], unit='m')
    with pytest.raises(ValueError, match="No finite values were found in array"):
        _ = find_limits(x)


def test_find_limits_all_zeros():
    x = sc.zeros(sizes={'x': 5}, unit='s')
    lims = find_limits(x)
    assert sc.identical(lims[0], sc.scalar(0.0, unit='s'))
    assert sc.identical(lims[1], sc.scalar(0.0, unit='s'))


def test_find_limits_all_zeros_log_uses_default_positive_values():
    x = sc.zeros(sizes={'x': 5}, unit='s')
    lims = find_limits(x, scale='log')
    zero = sc.scalar(0.0, unit='s')
    assert lims[0] > zero
    assert lims[1] > zero
    assert lims[0] < lims[1]


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
