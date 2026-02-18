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
        registry={
            'nyc_taxi_data.h5': 'md5:fc0867ec061e4ac0cbe5975a665a0eea',
            'teapot.h5': 'md5:012994ffc56f520589b921c2ce655c19',
            'air_temperature.h5': 'md5:453e919f14e58043753b756ce569a33d',
        },
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


def teapot() -> str:
    """
    Values extracted from the Utah teapot:
    https://graphics.cs.utah.edu/courses/cs6620/fall2013/?prj=5
    using PyWavefront https://pypi.org/project/PyWavefront/
    >> import pywavefront
    >> scene = pywavefront.Wavefront('path/to/teapot-low.obj', collect_faces=True)
    >> vertices = scene.vertices
    >> faces = scene.meshes[None].faces
    """
    return get_path('teapot.h5')


def air_temperature() -> str:
    """
    North American air temperature dataset from Xarray.
    See https://docs.xarray.dev/en/latest/user-guide/plotting.html
    """
    return get_path('air_temperature.h5')


def three_bands(
    npeaks: int = 200,
    per_peak: int = 500,
    spread: float = 30.0,
    seed: int | None = None,
) -> sc.DataArray:
    """
    Generate a 2D dataset with three bands of peaks.

    Parameters
    ----------
    npeaks:
        Number of peaks.
    per_peak:
        Number of points per peak.
    spread:
        Standard deviation (spread or 'width') of the peaks.
    seed:
        Random seed for reproducibility.
    """
    ny = 300
    nx = 300
    rng = np.random.default_rng(seed)
    shape = (npeaks, per_peak)
    x = np.empty(shape)
    y = np.empty(shape)
    xcenters = rng.uniform(0, nx, size=npeaks)
    ycenters = rng.choice([ny / 4, ny / 2, 3 * ny / 4], size=npeaks)
    spreads = rng.uniform(0, spread, size=npeaks)
    for i, (xc, yc, sp) in enumerate(zip(xcenters, ycenters, spreads, strict=True)):
        xy = np.random.normal(loc=(xc, yc), scale=sp, size=[per_peak, 2])
        x[i, :] = xy[:, 0]
        y[i, :] = xy[:, 1]

    xcoord = sc.array(dims=['row'], values=x.ravel(), unit='cm')
    ycoord = sc.array(dims=['row'], values=y.ravel(), unit='cm')
    table = sc.DataArray(
        data=sc.ones(sizes=xcoord.sizes, unit='counts'),
        coords={'x': xcoord, 'y': ycoord},
    )
    xedges = sc.linspace('x', -50, 350, num=nx + 1, unit='cm')
    yedges = sc.linspace('y', -50, 350, num=ny + 1, unit='cm')
    return table.hist(y=yedges, x=xedges) + sc.scalar(1.0, unit='counts')


def clusters3d(
    nclusters: int = 100, npercluster: int = 2000, seed: int | None = None
) -> sc.DataArray:
    """
    Generate a 3D dataset with clusters of points.

    Parameters
    ----------
    nclusters:
        Number of clusters.
    npercluster:
        Number of points per cluster.
    seed:
        Random seed for reproducibility.
    """
    position = np.zeros((nclusters, npercluster, 3))
    values = np.zeros((nclusters, npercluster))
    rng = np.random.default_rng(seed)

    for n in range(nclusters):
        center = 200.0 * (rng.random(3) - 0.5)
        r = 10.0 * rng.normal(size=[npercluster, 3])
        position[n, :] = r + center
        values[n, :] = 1 / np.linalg.norm(r, axis=1) ** 2

    out = sc.DataArray(
        data=sc.array(dims=['row'], values=values.flatten()),
        coords={
            'position': sc.vectors(
                dims=['row'],
                unit='m',
                values=position.reshape(nclusters * npercluster, 3),
            )
        },
    )
    return out.assign_coords(
        {c: getattr(out.coords['position'].fields, c).copy() for c in 'xyz'}
    )
