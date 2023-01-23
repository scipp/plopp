# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from typing import List, Optional

import numpy as np
import scipp as sc

default_dim_list = ['x', 'y', 'z', 'time', 'temperature']


def variable(ndim: int = 1,
             variances: bool = False,
             dtype: str = 'float64',
             unit: str = 'm/s',
             dims: Optional[List[str]] = None,
             dim_list: List[str] = default_dim_list) -> sc.Variable:
    """
    Generate a sample ``Variable`` containing data based on a sine function.

    Parameters
    ----------
    ndim:
        The number of dimensions.
    variances:
        Add variances to the output if ``True``.
    dtype:
        The output variable's data type.
    unit:
        The output variable's unit.
    dims:
        List of dimension labels. If ``None``, they will be auto-generated.
    dim_list:
        List of dimension labels to use if no ``dims`` are provided.
    """

    shapes = np.arange(50, 0, -10)[:ndim]
    if dims is None:
        dims = dim_list[:ndim][::-1]

    axes = [np.arange(shape, dtype=np.float64) for shape in shapes]
    pos = np.meshgrid(*axes, indexing='ij')
    radius = np.linalg.norm(np.array(pos), axis=0)
    a = np.sin(radius / 5.0)

    var = sc.array(dims=dims, values=a, unit=unit, dtype=dtype)
    if variances:
        var.variances = np.abs(np.random.normal(a * 0.1, 0.05))

    return var


def data_array(ndim: int = 1,
               variances: bool = False,
               binedges: bool = False,
               labels: bool = False,
               masks: bool = False,
               attrs: bool = False,
               ragged: bool = False,
               dtype: str = 'float64',
               unit: str = 'm/s',
               dims: Optional[List[str]] = None,
               dim_list: List[str] = default_dim_list) -> sc.DataArray:
    """
    Generate a sample ``DataArray`` containing data based on a sine function, with
    coordinates. Optionally add masks, labels, attributes.
    It is also possible to turn the coordinates into bin-edges, or make a ragged (2d)
    coordinate.

    Parameters
    ----------
    ndim:
        The number of dimensions.
    variances:
        Add variances to the output if ``True``.
    binedges:
        The output will have bin-edge coordinates instead of bin-centers if ``True``.
    labels:
        Add non-dimension coordinates if ``True``.
    masks:
        Add masks if ``True``.
    attrs:
        Add attributes if ``True``.
    ragged:
        Make one of the coordinates two-dimensional.
    dtype:
        The output variable's data type.
    unit:
        The output variable's unit.
    dims:
        List of dimension labels. If ``None``, they will be auto-generated.
    dim_list:
        List of dimension labels to use if no ``dims`` are provided.
    """

    coord_units = dict(zip(dim_list, ['m', 'm', 'm', 's', 'K']))

    data = variable(ndim=ndim,
                    variances=variances,
                    dims=dims,
                    dtype=dtype,
                    unit=unit,
                    dim_list=dim_list)

    coord_dict = {
        data.dims[i]: sc.arange(data.dims[i],
                                data.shape[i] + binedges,
                                unit=coord_units[data.dims[i]],
                                dtype=np.float64)
        for i in range(ndim)
    }
    attr_dict = {}
    mask_dict = {}

    if labels:
        coord_dict["lab"] = sc.linspace(data.dims[0],
                                        101.,
                                        105.,
                                        data.shape[0],
                                        unit='s')
    if attrs:
        attr_dict["attr"] = sc.linspace(data.dims[0], 10., 77., data.shape[0], unit='s')
    if masks:
        mask_dict["mask"] = sc.array(dims=data.dims,
                                     values=np.where(data.values > 0, True, False))

    if ragged:
        grid = []
        for i, dim in enumerate(data.dims):
            if binedges and (i < ndim - 1):
                grid.append(coord_dict[dim].values[:-1])
            else:
                grid.append(coord_dict[dim].values)
        mesh = np.meshgrid(*grid, indexing="ij")
        coord_dict[data.dims[-1]] = sc.array(dims=data.dims,
                                             values=mesh[-1] +
                                             np.indices(mesh[-1].shape)[0])
    return sc.DataArray(data=data, coords=coord_dict, attrs=attr_dict, masks=mask_dict)


def dataset(entries: List[str] = None, **kwargs) -> sc.Dataset:
    """
    Generate a sample ``Dataset``. See :func:`data_array` for more options.

    Parameters
    ----------
    entries:
        A list of names for the elements of the dataset.
    **kwargs:
        All other keyword arguments are forwarded to :func:`data_array`.
    """
    if entries is None:
        entries = ['a', 'b']
    ds = sc.Dataset()
    for entry in entries:
        ds[entry] = (10.0 * np.random.random()) * data_array(**kwargs)
    return ds


def scatter(npoints=500, scale=10.0, seed=1) -> sc.DataArray:
    """
    Generate some three-dimensional scatter data, based on a normal distribution.

    Parameters
    ----------
    npoints:
        The number of points to generate.
    scale:
        Standard deviation (spread or 'width') of the distribution.
    seed:
        The seed for the random number generator.
    """
    rng = np.random.default_rng(seed)
    position = scale * rng.standard_normal(size=[npoints, 3])
    values = np.linalg.norm(position, axis=1)
    vec = sc.vectors(dims=['row'], unit='m', values=position)
    return sc.DataArray(data=sc.array(dims=['row'], values=values, unit='K'),
                        coords={
                            'position': vec,
                            'x': vec.fields.x,
                            'y': vec.fields.y,
                            'z': vec.fields.z
                        })


def data1d(**kwargs):
    return data_array(ndim=1, **kwargs)


def data2d(**kwargs):
    return data_array(ndim=2, **kwargs)


def data3d(**kwargs):
    return data_array(ndim=3, **kwargs)


def histogram1d(**kwargs):
    return data_array(ndim=1, binedges=True, **kwargs)


def histogram2d(**kwargs):
    return data_array(ndim=2, binedges=True, **kwargs)


def histogram3d(**kwargs):
    return data_array(ndim=3, binedges=True, **kwargs)


def dataset1d(**kwargs):
    return dataset(ndim=1, **kwargs)


def dataset2d(**kwargs):
    return dataset(ndim=2, **kwargs)
