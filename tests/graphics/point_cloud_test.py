# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.data import scatter_data
from plopp.graphics.point_cloud import PointCloud

import numpy as np
import scipp as sc
import ipywidgets as ipw


def test_creation():
    da = scatter_data()
    cloud = PointCloud(data=da, x='x', y='y', z='z', cbar=ipw.VBox(), figsize=(8, 6))
    assert sc.identical(cloud._data, da)
    assert np.allclose(cloud.geometry.attributes['position'].array,
                       da.coords['position'].values)
    assert np.allclose(cloud.geometry.attributes['color'].array,
                       cloud.color_mapper.rgba(da)[..., :3])


def test_toggle_norm():
    da = scatter_data()
    cloud = PointCloud(data=da, x='x', y='y', z='z', cbar=ipw.VBox(), figsize=(8, 6))
    assert cloud.color_mapper.norm_flag == 'linear'
    cloud.toggle_norm()
    assert cloud.color_mapper.norm_flag == 'log'
    cloud.toggle_norm()
    assert cloud.color_mapper.norm_flag == 'linear'


def test_update():
    da = scatter_data()
    cloud = PointCloud(data=da, x='x', y='y', z='z', cbar=ipw.VBox(), figsize=(8, 6))
    old_image = cloud.colorbar['image'].value
    cloud.update(da)
    assert sc.identical(cloud._data, da)
    # Update with the same values should not make a new colorbar image
    assert old_image is cloud.colorbar['image'].value
    cloud.update(da * 2.5)
    assert sc.identical(cloud._data, da * 2.5)
    assert old_image != cloud.colorbar['image'].value


def test_get_limits():
    da = scatter_data()
    cloud = PointCloud(data=da, x='x', y='y', z='z', cbar=ipw.VBox(), figsize=(8, 6))
    xlims, ylims, zlims = cloud.get_limits()
    assert sc.identical(xlims[0], da.meta['x'].min())
    assert sc.identical(xlims[1], da.meta['x'].max())
    assert sc.identical(ylims[0], da.meta['y'].min())
    assert sc.identical(ylims[1], da.meta['y'].max())
    assert sc.identical(zlims[0], da.meta['z'].min())
    assert sc.identical(zlims[1], da.meta['z'].max())
