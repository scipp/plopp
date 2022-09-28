# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.data import dense_data_array
from plopp.graphics.color_mapper import ColorMapper
import scipp as sc
import numpy as np
from common import make_axes
from dataclasses import dataclass
from matplotlib.colors import Normalize, LogNorm


def test_creation():
    mapper = ColorMapper(cmap='magma',
                         mask_cmap='jet',
                         norm='linear',
                         vmin=sc.scalar(1, unit='K'),
                         vmax=sc.scalar(10, unit='K'))
    assert mapper.cmap.name == 'magma'
    assert mapper.mask_cmap.name == 'jet'
    assert mapper.norm_flag == 'linear'
    assert sc.identical(mapper.user_vmin, sc.scalar(1, unit='K'))
    assert sc.identical(mapper.user_vmax, sc.scalar(10, unit='K'))


def test_toggle_norm():
    from matplotlib.colors import Normalize, LogNorm
    mapper = ColorMapper()
    assert mapper.norm_flag == 'linear'
    mapper.toggle_norm()
    assert mapper.norm_flag == 'log'
    mapper.toggle_norm()
    assert mapper.norm_flag == 'linear'


def test_set_norm():
    da = dense_data_array(ndim=2, unit='K') + sc.scalar(10.0, unit='K')
    mapper = ColorMapper()

    mapper.set_norm(data=da)
    assert isinstance(mapper.norm_func, Normalize)
    assert mapper.vmin == da.min().value
    assert mapper.vmax == da.max().value
    assert mapper.norm_func.vmin == da.min().value
    assert mapper.norm_func.vmax == da.max().value

    mapper.toggle_norm()
    mapper.set_norm(data=da)
    assert isinstance(mapper.norm_func, LogNorm)
    assert mapper.vmin == da.min().value
    assert mapper.vmax == da.max().value
    assert mapper.norm_func.vmin == da.min().value
    assert mapper.norm_func.vmax == da.max().value


def test_rescale():
    da = dense_data_array(ndim=2, unit='K')
    mapper = ColorMapper()

    mapper.set_norm(data=da)
    assert mapper.vmin == da.min().value
    assert mapper.vmax == da.max().value
    assert mapper.norm_func.vmin == da.min().value
    assert mapper.norm_func.vmax == da.max().value

    const = 2.3
    mapper.set_norm(data=da * const)
    assert mapper.vmin == (da.min() * const).value
    assert mapper.vmax == (da.max() * const).value
    assert mapper.norm_func.vmin == (da.min() * const).value
    assert mapper.norm_func.vmax == (da.max() * const).value


def test_rescale_limits_do_not_shrink():
    da = dense_data_array(ndim=2, unit='K')
    mapper = ColorMapper()

    mapper.set_norm(data=da)
    assert mapper.vmin == da.min().value
    assert mapper.vmax == da.max().value
    assert mapper.norm_func.vmin == da.min().value
    assert mapper.norm_func.vmax == da.max().value

    const = 0.5
    mapper.set_norm(data=da * const)
    assert mapper.vmin == da.min().value
    assert mapper.vmax == da.max().value
    assert mapper.norm_func.vmin == da.min().value
    assert mapper.norm_func.vmax == da.max().value


def test_vmin_vmax():
    da = dense_data_array(ndim=2, unit='K')
    vmin = sc.scalar(-0.1, unit='K')
    vmax = sc.scalar(3.5, unit='K')
    mapper = ColorMapper(vmin=vmin, vmax=vmax)
    mapper.set_norm(data=da)
    assert sc.identical(mapper.user_vmin, vmin)
    assert sc.identical(mapper.user_vmax, vmax)
    assert mapper.vmin == vmin.value
    assert mapper.vmax == vmax.value
    assert mapper.norm_func.vmin == vmin.value
    assert mapper.norm_func.vmax == vmax.value


def test_rgba():
    da = dense_data_array(ndim=2, unit='K')
    mapper = ColorMapper()
    mapper.set_norm(data=da.data)
    colors = mapper.rgba(da)
    assert colors.shape == da.data.shape + (4, )


def test_rgba_with_masks():
    da1 = dense_data_array(ndim=2, unit='K')
    da2 = dense_data_array(ndim=2, unit='K', masks=True)
    mapper = ColorMapper()
    mapper.set_norm(data=da1.data)
    assert not np.allclose(mapper.rgba(da1), mapper.rgba(da2))
