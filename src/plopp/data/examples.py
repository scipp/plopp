# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from functools import lru_cache

_version = '1'


@lru_cache(maxsize=1)
def _make_pooch():
    import pooch
    return pooch.create(
        path=pooch.os_cache('plopp'),
        env='PLOPP_DATA_DIR',
        base_url='https://public.esss.dk/groups/scipp/plopp/{version}/',
        version=_version,
        registry={'nyc_taxi_data.h5': 'md5:fc0867ec061e4ac0cbe5975a665a0eea'})


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
