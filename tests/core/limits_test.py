# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.core.limits import find_limits, fix_empty_range
import scipp as sc
import numpy as np


def test_find_limits():
    x = sc.arange('x', 11., unit='m')
    lims = find_limits(x)
    assert sc.identical(lims[0], sc.scalar(0., unit='m'))
    assert sc.identical(lims[1], sc.scalar(10., unit='m'))


def test_find_limits_log():
    x = sc.arange('x', 11., unit='m')
    lims = find_limits(x, scale='log')
    assert sc.identical(lims[0], sc.scalar(1., unit='m'))
    assert sc.identical(lims[1], sc.scalar(10., unit='m'))


def test_find_limits_with_nan():
    x = sc.arange('x', 11., unit='m')
    x.values[5] = np.nan
    lims = find_limits(x)
    assert sc.identical(lims[0], sc.scalar(0., unit='m'))
    assert sc.identical(lims[1], sc.scalar(10., unit='m'))


def test_find_limits_with_ninf():
    x = sc.arange('x', 11., unit='m')
    x.values[5] = np.NINF
    lims = find_limits(x)
    assert sc.identical(lims[0], sc.scalar(0., unit='m'))
    assert sc.identical(lims[1], sc.scalar(10., unit='m'))


def test_fix_empty_range():
    a = sc.scalar(5., unit='m')
    b = sc.scalar(10., unit='m')
    lims = fix_empty_range((a, b))
    assert sc.identical(lims[0], a)
    assert sc.identical(lims[1], b)


def test_fix_empty_range_same_values():
    a = sc.scalar(5., unit='m')
    lims = fix_empty_range((a, a))
    assert sc.identical(lims[0], sc.scalar(2.5, unit='m'))
    assert sc.identical(lims[1], sc.scalar(7.5, unit='m'))
    lims = fix_empty_range((-a, -a))
    assert sc.identical(lims[0], sc.scalar(-7.5, unit='m'))
    assert sc.identical(lims[1], sc.scalar(-2.5, unit='m'))


def test_fix_empty_range_zeros_values():
    a = sc.scalar(0., unit='m')
    lims = fix_empty_range((a, a))
    assert sc.identical(lims[0], sc.scalar(-0.5, unit='m'))
    assert sc.identical(lims[1], sc.scalar(0.5, unit='m'))
