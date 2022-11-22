# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.data.testing import scatter_data
from plopp.graphics.point_cloud import PointCloud

import numpy as np
import scipp as sc


def test_creation():
    da = scatter_data()
    cloud = PointCloud(data=da, x='x', y='y', z='z')
    assert sc.identical(cloud._data, da)
    assert np.allclose(cloud.geometry.attributes['position'].array,
                       da.coords['position'].values)


def test_update():
    da = scatter_data()
    cloud = PointCloud(data=da, x='x', y='y', z='z')
    cloud.update(da)
    assert sc.identical(cloud._data, da)
    cloud.update(da * 2.5)
    assert sc.identical(cloud._data, da * 2.5)


def test_get_limits():
    da = scatter_data()
    pix = 0.5
    cloud = PointCloud(data=da, x='x', y='y', z='z', pixel_size=pix)
    xlims, ylims, zlims = cloud.get_limits()
    assert sc.identical(xlims[0], da.meta['x'].min() - sc.scalar(0.5 * pix, unit='m'))
    assert sc.identical(xlims[1], da.meta['x'].max() + sc.scalar(0.5 * pix, unit='m'))
    assert sc.identical(ylims[0], da.meta['y'].min() - sc.scalar(0.5 * pix, unit='m'))
    assert sc.identical(ylims[1], da.meta['y'].max() + sc.scalar(0.5 * pix, unit='m'))
    assert sc.identical(zlims[0], da.meta['z'].min() - sc.scalar(0.5 * pix, unit='m'))
    assert sc.identical(zlims[1], da.meta['z'].max() + sc.scalar(0.5 * pix, unit='m'))


def test_get_limits_flat_panel():
    da = scatter_data()
    da.coords['z'] *= 0.
    pix = 0.5
    cloud = PointCloud(data=da, x='x', y='y', z='z', pixel_size=pix)
    xlims, ylims, zlims = cloud.get_limits()
    assert sc.identical(xlims[0], da.meta['x'].min() - sc.scalar(0.5 * pix, unit='m'))
    assert sc.identical(xlims[1], da.meta['x'].max() + sc.scalar(0.5 * pix, unit='m'))
    assert sc.identical(ylims[0], da.meta['y'].min() - sc.scalar(0.5 * pix, unit='m'))
    assert sc.identical(ylims[1], da.meta['y'].max() + sc.scalar(0.5 * pix, unit='m'))
    assert sc.identical(zlims[0], sc.scalar(-0.5 * pix, unit='m'))
    assert sc.identical(zlims[1], sc.scalar(0.5 * pix, unit='m'))
