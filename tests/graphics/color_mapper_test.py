# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.data import dense_data_array
from plopp.graphics.color_mapper import ColorMapper
import scipp as sc
import numpy as np
from matplotlib.colors import Normalize, LogNorm


def test_creation():
    mapper = ColorMapper(cmap='magma',
                         mask_cmap='jet',
                         norm='linear',
                         vmin=sc.scalar(1, unit='K'),
                         vmax=sc.scalar(10, unit='K'),
                         notify_on_change=lambda: None)
    assert mapper.cmap.name == 'magma'
    assert mapper.mask_cmap.name == 'jet'
    assert mapper._norm == 'linear'
    assert sc.identical(mapper.user_vmin, sc.scalar(1, unit='K'))
    assert sc.identical(mapper.user_vmax, sc.scalar(10, unit='K'))


def test_toggle_norm():
    mapper = ColorMapper(notify_on_change=lambda: None)
    assert mapper._norm == 'linear'
    mapper.toggle_norm()
    assert mapper._norm == 'log'
    mapper.toggle_norm()
    assert mapper._norm == 'linear'


def test_set_norm():
    da = dense_data_array(ndim=2, unit='K') + sc.scalar(10.0, unit='K')
    mapper = ColorMapper(notify_on_change=lambda: None)

    mapper.set_norm(data=da)
    assert isinstance(mapper.norm, Normalize)
    assert mapper.vmin == da.min().value
    assert mapper.vmax == da.max().value
    assert mapper.norm.vmin == da.min().value
    assert mapper.norm.vmax == da.max().value

    mapper.toggle_norm()
    mapper.set_norm(data=da)
    assert isinstance(mapper.norm, LogNorm)
    assert mapper.vmin == da.min().value
    assert mapper.vmax == da.max().value
    assert mapper.norm.vmin == da.min().value
    assert mapper.norm.vmax == da.max().value


def test_rescale():
    da = dense_data_array(ndim=2, unit='K')
    mapper = ColorMapper(notify_on_change=lambda: None)

    mapper.set_norm(data=da)
    assert mapper.vmin == da.min().value
    assert mapper.vmax == da.max().value
    assert mapper.norm.vmin == da.min().value
    assert mapper.norm.vmax == da.max().value

    const = 2.3
    mapper.set_norm(data=da * const)
    assert mapper.vmin == (da.min() * const).value
    assert mapper.vmax == (da.max() * const).value
    assert mapper.norm.vmin == (da.min() * const).value
    assert mapper.norm.vmax == (da.max() * const).value


def test_rescale_limits_do_not_shrink():
    da = dense_data_array(ndim=2, unit='K')
    mapper = ColorMapper(notify_on_change=lambda: None)

    mapper.set_norm(data=da)
    assert mapper.vmin == da.min().value
    assert mapper.vmax == da.max().value
    assert mapper.norm.vmin == da.min().value
    assert mapper.norm.vmax == da.max().value

    const = 0.5
    mapper.set_norm(data=da * const)
    assert mapper.vmin == da.min().value
    assert mapper.vmax == da.max().value
    assert mapper.norm.vmin == da.min().value
    assert mapper.norm.vmax == da.max().value


def test_vmin_vmax():
    da = dense_data_array(ndim=2, unit='K')
    vmin = sc.scalar(-0.1, unit='K')
    vmax = sc.scalar(3.5, unit='K')
    mapper = ColorMapper(vmin=vmin, vmax=vmax, notify_on_change=lambda: None)
    mapper.set_norm(data=da)
    assert sc.identical(mapper.user_vmin, vmin)
    assert sc.identical(mapper.user_vmax, vmax)
    assert mapper.vmin == vmin.value
    assert mapper.vmax == vmax.value
    assert mapper.norm.vmin == vmin.value
    assert mapper.norm.vmax == vmax.value


def test_rgba():
    da = dense_data_array(ndim=2, unit='K')
    mapper = ColorMapper(notify_on_change=lambda: None)
    mapper.set_norm(data=da)
    colors = mapper.rgba(da)
    assert colors.shape == da.data.shape + (4, )


def test_rgba_with_masks():
    da1 = dense_data_array(ndim=2, unit='K')
    da2 = dense_data_array(ndim=2, unit='K', masks=True)
    mapper = ColorMapper(notify_on_change=lambda: None)
    mapper.set_norm(data=da1)
    assert not np.allclose(mapper.rgba(da1), mapper.rgba(da2))


def test_colorbar_updated_on_rescale():
    da = dense_data_array(ndim=2, unit='K')
    mapper = ColorMapper(notify_on_change=lambda: None)

    mapper.set_norm(data=da)
    w = mapper.widget
    old_image = mapper.colorbar['image'].value
    old_image_array = bytearray(old_image)

    # Update with the same values should not make a new colorbar image
    mapper.rescale(data=da)
    assert old_image is mapper.colorbar['image'].value

    const = 2.3
    mapper.rescale(data=da * const)
    assert old_image_array != bytearray(mapper.colorbar['image'].value)
