# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from functools import lru_cache

import numpy as np
import scipp as sc

_version = '1'


@lru_cache(maxsize=1)
def _make_pooch():
    import pooch

    return pooch.create(
        path=pooch.os_cache('plopp'),
        env='PLOPP_DATA_DIR',
        base_url='https://public.esss.dk/groups/scipp/plopp/{version}/',
        version=_version,
        registry={'nyc_taxi_data.h5': 'md5:fc0867ec061e4ac0cbe5975a665a0eea'},
    )


_pooch = _make_pooch()


def get_path(name: str) -> str:
    """
    Return the path to a data file bundled with plopp.

    This function only works with example data and cannot handle
    paths to custom files.
    """
    return _pooch.fetch(name)


def nyc_taxi() -> str:
    """
    Return the path to the NYC taxi dataset from 2015 histogrammed in latitude,
    longitude, and hour-of-the-dat, stored in scipp's HDF5 format.

    The original data was found at https://vaex.readthedocs.io/en/latest/datasets.html.

    Attention
    ---------
    This data has been manipulated!
    """
    return get_path('nyc_taxi_data.h5')


def three_bands():
    """
    Generate a 2D dataset with three bands of peaks.
    """
    npeaks = 200
    per_peak = 500
    spread = 30.0
    ny = 300
    nx = 300
    rng = np.random.default_rng()
    shape = (npeaks, per_peak)
    x = np.empty(shape)
    y = np.empty(shape)
    xcenters = rng.uniform(0, nx, size=npeaks)
    ycenters = rng.choice([ny / 4, ny / 2, 3 * ny / 4], size=npeaks)
    spreads = rng.uniform(0, spread, size=npeaks)
    for i, (xc, yc, sp) in enumerate(zip(xcenters, ycenters, spreads)):
        xy = np.random.normal(loc=(xc, yc), scale=sp, size=[per_peak, 2])
        x[i, :] = xy[:, 0]
        y[i, :] = xy[:, 1]

    xcoord = sc.array(dims=['row'], values=x.ravel(), unit='cm')
    ycoord = sc.array(dims=['row'], values=y.ravel(), unit='cm')
    table = sc.DataArray(
        data=sc.ones(sizes=xcoord.sizes, unit='counts'),
        coords={'x': xcoord, 'y': ycoord},
    )
    return table.hist(y=300, x=300) + sc.scalar(1.0, unit='counts')
