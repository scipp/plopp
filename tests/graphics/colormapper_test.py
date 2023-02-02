# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from dataclasses import dataclass

import numpy as np
import scipp as sc
from matplotlib.colors import LogNorm, Normalize

from plopp.data.testing import data_array
from plopp.graphics.colormapper import ColorMapper


class DummyChild:

    def __init__(self, data):
        self._data = data
        self._colors = None

    def set_colors(self, colors):
        self._colors = colors

    @property
    def data(self):
        return self._data


def test_creation():
    mapper = ColorMapper(cmap='magma',
                         mask_cmap='jet',
                         norm='linear',
                         vmin=sc.scalar(1, unit='K'),
                         vmax=sc.scalar(10, unit='K'))
    assert mapper.cmap.name == 'magma'
    assert mapper.mask_cmap.name == 'jet'
    assert mapper.norm == 'linear'
    assert sc.identical(mapper.user_vmin, sc.scalar(1, unit='K'))
    assert sc.identical(mapper.user_vmax, sc.scalar(10, unit='K'))


def test_norm():
    mapper = ColorMapper(norm='log')
    assert mapper.norm == 'log'


def test_autoscale():
    da = data_array(ndim=2, unit='K')
    mapper = ColorMapper()

    mapper.autoscale(data=da)
    assert mapper.vmin == da.min().value
    assert mapper.vmax == da.max().value

    const = 2.3
    mapper.autoscale(data=da * const)
    assert mapper.vmin == (da.min() * const).value
    assert mapper.vmax == (da.max() * const).value


def test_rescale_limits_do_not_shrink():
    da = data_array(ndim=2, unit='K')
    mapper = ColorMapper()

    mapper.autoscale(data=da)
    assert mapper.vmin == da.min().value
    assert mapper.vmax == da.max().value

    const = 0.5
    mapper.autoscale(data=da * const)
    assert mapper.vmin == da.min().value
    assert mapper.vmax == da.max().value


def test_vmin_vmax():
    da = data_array(ndim=2, unit='K')
    vmin = sc.scalar(-0.1, unit='K')
    vmax = sc.scalar(3.5, unit='K')
    mapper = ColorMapper(vmin=vmin, vmax=vmax)
    mapper.update(data=da * 100., key=None)
    assert sc.identical(mapper.user_vmin, vmin)
    assert sc.identical(mapper.user_vmax, vmax)
    assert mapper.vmin == vmin.value
    assert mapper.vmax == vmax.value


def test_vmin_vmax_no_variable():
    da = data_array(ndim=2, unit='K')
    vmin = -0.1
    vmax = 3.5
    mapper = ColorMapper(vmin=vmin, vmax=vmax)
    mapper.update(data=da * 100., key=None)
    assert mapper.user_vmin == vmin
    assert mapper.user_vmax == vmax
    assert mapper.vmin == vmin
    assert mapper.vmax == vmax


def test_toggle_norm():
    mapper = ColorMapper()
    da = data_array(ndim=2, unit='K')
    mapper['child1'] = DummyChild(da)
    mapper.autoscale(da)
    assert mapper.norm == 'linear'
    assert isinstance(mapper.normalizer, Normalize)
    assert mapper.vmin == da.min().value
    assert mapper.vmax == da.max().value

    mapper.toggle_norm()
    assert mapper.norm == 'log'
    assert isinstance(mapper.normalizer, LogNorm)
    assert mapper.vmin > 0
    assert mapper.vmax == da.max().value


def test_update_changes_limits():
    da = data_array(ndim=2, unit='K')
    mapper = ColorMapper()

    mapper.update(data=da, key=None)
    assert mapper.normalizer.vmin == da.min().value
    assert mapper.normalizer.vmax == da.max().value

    const = 2.3
    mapper.update(data=da * const, key=None)
    assert mapper.normalizer.vmin == (da.min() * const).value
    assert mapper.normalizer.vmax == (da.max() * const).value


def test_rgba():
    da = data_array(ndim=2, unit='K')
    mapper = ColorMapper()
    colors = mapper.rgba(da)
    assert colors.shape == da.data.shape + (4, )


def test_rgba_with_masks():
    da1 = data_array(ndim=2, unit='K')
    da2 = data_array(ndim=2, unit='K', masks=True)
    mapper = ColorMapper()
    assert not np.allclose(mapper.rgba(da1), mapper.rgba(da2))


def test_colorbar_updated_on_rescale():
    da = data_array(ndim=2, unit='K')
    mapper = ColorMapper()

    mapper.update(data=da, key=None)
    _ = mapper.to_widget()
    old_image = mapper.widget.value
    old_image_array = old_image

    # Update with the same values should not make a new colorbar image
    mapper.update(data=da, key=None)
    assert old_image is mapper.widget.value

    const = 2.3
    mapper.update(data=da * const, key=None)
    assert old_image_array != mapper.widget.value


def test_colorbar_is_not_created_if_cbar_false():
    mapper = ColorMapper(cbar=False)
    assert mapper.colorbar is None
    assert mapper.cax is None


def test_colorbar_cbar_false_overrides_cax():

    @dataclass
    class Canvas:
        cax: int

    mapper = ColorMapper(cbar=False, canvas=Canvas(cax=0))
    assert mapper.colorbar is None
