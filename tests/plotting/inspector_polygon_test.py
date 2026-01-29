# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Scipp contributors (https://github.com/scipp)

import numpy as np
import scipp as sc


def _make_da() -> sc.DataArray:
    data = sc.array(
        dims=['y', 'x', 'z'],
        values=np.arange(2 * 3 * 4, dtype=float).reshape(2, 3, 4),
    )
    coords = {
        'x': sc.arange('x', 3),
        'y': sc.arange('y', 2),
        'z': sc.arange('z', 4),
    }
    return sc.DataArray(data=data, coords=coords)


def test_slice_polygon_sum_full_selection():
    import plopp as pp
    from plopp.plotting.inspector import _slice_polygon

    _ = pp.inspector
    da = _make_da()
    poly = {
        'x': {
            'dim': 'x',
            'value': sc.array(dims=['vertex'], values=[-1.0, 3.0, 3.0, -1.0]),
        },
        'y': {
            'dim': 'y',
            'value': sc.array(dims=['vertex'], values=[-1.0, -1.0, 2.0, 2.0]),
        },
    }

    out = _slice_polygon(da, poly, 'sum')
    expected = sc.nansum(da, dim=['y', 'x'])
    assert sc.identical(out, expected)


def test_slice_polygon_min_empty_selection_is_nan():
    import plopp as pp
    from plopp.plotting.inspector import _slice_polygon

    _ = pp.inspector
    da = _make_da()
    poly = {
        'x': {
            'dim': 'x',
            'value': sc.array(dims=['vertex'], values=[10.0, 11.0, 11.0, 10.0]),
        },
        'y': {
            'dim': 'y',
            'value': sc.array(dims=['vertex'], values=[10.0, 10.0, 11.0, 11.0]),
        },
    }

    out = _slice_polygon(da, poly, 'min')
    assert sc.all(sc.isnan(out.data)).value


def test_slice_polygon_max_empty_selection_is_nan():
    import plopp as pp
    from plopp.plotting.inspector import _slice_polygon

    _ = pp.inspector
    da = _make_da()
    poly = {
        'x': {
            'dim': 'x',
            'value': sc.array(dims=['vertex'], values=[10.0, 11.0, 11.0, 10.0]),
        },
        'y': {
            'dim': 'y',
            'value': sc.array(dims=['vertex'], values=[10.0, 10.0, 11.0, 11.0]),
        },
    }

    out = _slice_polygon(da, poly, 'max')
    assert sc.all(sc.isnan(out.data)).value


def test_slice_polygon_mean_empty_selection_is_nan():
    import plopp as pp
    from plopp.plotting.inspector import _slice_polygon

    _ = pp.inspector
    da = _make_da()
    poly = {
        'x': {
            'dim': 'x',
            'value': sc.array(dims=['vertex'], values=[10.0, 11.0, 11.0, 10.0]),
        },
        'y': {
            'dim': 'y',
            'value': sc.array(dims=['vertex'], values=[10.0, 10.0, 11.0, 11.0]),
        },
    }

    out = _slice_polygon(da, poly, 'mean')
    assert sc.all(sc.isnan(out.data)).value
