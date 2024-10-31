# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from dataclasses import dataclass
from difflib import SequenceMatcher
from functools import partial

import numpy as np
import pytest
import scipp as sc
from matplotlib.colors import LogNorm, Normalize

from plopp import Node, imagefigure, scatter3dfigure
from plopp.data.testing import data_array, scatter
from plopp.graphics.colormapper import ColorMapper


def string_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


class DummyChild:
    def __init__(self, data, colormapper):
        self._data = data
        self._colormapper = colormapper
        self._colors = None

    def notify_artist(self, _):
        self._update_colors()

    def _update_colors(self):
        self._colors = self._colormapper.rgba(self._data)

    def update(self, data):
        self._data = data
        self._update_colors()

    @property
    def data(self):
        return self._data


def test_creation():
    mapper = ColorMapper(
        cmap='magma',
        mask_cmap='jet',
        norm='linear',
    )
    assert mapper.cmap.name == 'magma'
    assert mapper.mask_cmap.name == 'jet'
    assert mapper.norm == 'linear'


def test_norm():
    mapper = ColorMapper(norm='log')
    assert mapper.norm == 'log'


def test_autoscale():
    da = data_array(ndim=2, unit='K')
    mapper = ColorMapper()
    artist = DummyChild(data=da, colormapper=mapper)
    mapper.add_artist('data', artist)

    mapper.autoscale()
    assert mapper.vmin == da.min().value
    assert mapper.vmax == da.max().value

    # Limits grow
    const = 2.3
    artist.update(da * const)
    mapper.autoscale()
    assert mapper.vmin == (da.min() * const).value
    assert mapper.vmax == (da.max() * const).value

    # Limits shrink
    const = 0.5
    artist.update(da * const)
    mapper.autoscale()
    assert mapper.vmin == da.min().value * const
    assert mapper.vmax == da.max().value * const


def test_update_without_autoscale_does_not_change_limits():
    da = data_array(ndim=2, unit='K')
    mapper = ColorMapper()
    artist = DummyChild(data=da, colormapper=mapper)
    mapper.add_artist('data', artist)

    mapper.autoscale()
    assert mapper.vmin == da.min().value
    assert mapper.vmax == da.max().value

    backup = mapper.vmin, mapper.vmax

    # Limits grow
    const = 2.3
    artist.update(da * const)
    assert mapper.vmin != (da.min() * const).value
    assert mapper.vmin == backup[0]
    assert mapper.vmax != (da.max() * const).value
    assert mapper.vmax == backup[1]

    # Limits shrink
    const = 0.5
    artist.update(da * const)
    assert mapper.vmin != da.min().value * const
    assert mapper.vmin == backup[0]
    assert mapper.vmax != da.max().value * const
    assert mapper.vmax == backup[1]


def test_correct_normalizer_limits():
    da = sc.DataArray(data=sc.array(dims=['y', 'x'], values=[[1, 2], [3, 4]]))
    mapper = ColorMapper()
    artist = DummyChild(data=da, colormapper=mapper)
    mapper.add_artist('data', artist)
    mapper.autoscale()
    assert mapper.vmin == da.min().value
    assert mapper.vmax == da.max().value
    # The normalizer initially has limits [0, 1].
    # In Matplotlib, if we set the normalizer vmin value (1) equal to the current vmax,
    # it will silently set it to something smaller, e.g. 0.9.
    # Our implementation needs to work around this.
    assert mapper.normalizer.vmin == da.min().value
    assert mapper.normalizer.vmax == da.max().value


def test_vmin_vmax():
    da = data_array(ndim=2, unit='K') * 100.0
    vmin = sc.scalar(-0.1, unit='K')
    vmax = sc.scalar(3.5, unit='K')
    mapper = ColorMapper(vmin=vmin, vmax=vmax)
    artist = DummyChild(data=da, colormapper=mapper)
    mapper.add_artist('data', artist)
    mapper.unit = 'K'
    mapper.autoscale()
    assert mapper.user_vmin == vmin.value
    assert mapper.user_vmax == vmax.value
    assert mapper.vmin == vmin.value
    assert mapper.vmax == vmax.value


def test_vmin_vmax_no_variable():
    da = data_array(ndim=2, unit='K') * 100.0
    vmin = -0.1
    vmax = 3.5
    mapper = ColorMapper(vmin=vmin, vmax=vmax)
    artist = DummyChild(data=da, colormapper=mapper)
    mapper.add_artist('data', artist)
    mapper.unit = 'K'
    mapper.autoscale()
    assert mapper.user_vmin == vmin
    assert mapper.user_vmax == vmax
    assert mapper.vmin == vmin
    assert mapper.vmax == vmax


def test_toggle_norm():
    mapper = ColorMapper()
    da = data_array(ndim=2, unit='K')
    mapper.add_artist('child1', DummyChild(data=da, colormapper=mapper))
    mapper.autoscale()
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
    artist = DummyChild(data=da, colormapper=mapper)
    mapper.add_artist('data', artist)

    mapper.autoscale()
    assert mapper.normalizer.vmin == da.min().value
    assert mapper.normalizer.vmax == da.max().value

    const = 2.3
    artist.update(da * const)
    mapper.autoscale()
    assert mapper.normalizer.vmin == (da.min() * const).value
    assert mapper.normalizer.vmax == (da.max() * const).value


def test_rgba():
    da = data_array(ndim=2, unit='K')
    mapper = ColorMapper()
    colors = mapper.rgba(da)
    assert colors.shape == (*da.data.shape, 4)


def test_rgba_with_masks():
    da1 = data_array(ndim=2, unit='K')
    da2 = data_array(ndim=2, unit='K', masks=True)
    mapper = ColorMapper()
    assert not np.allclose(mapper.rgba(da1), mapper.rgba(da2))


def test_colorbar_updated_on_rescale():
    da = data_array(ndim=2, unit='K')
    mapper = ColorMapper()
    artist = DummyChild(data=da, colormapper=mapper)
    mapper.add_artist('data', artist)

    mapper.autoscale()
    _ = mapper.to_widget()
    old_image = mapper.widget.value
    old_image_array = old_image

    # Update with the same values should not make a new colorbar image
    artist.update(da)
    mapper.autoscale()
    assert string_similarity(old_image_array, mapper.widget.value) > 0.9

    # Update with a smaller range should make a new colorbar image
    artist.update(da * 0.6)
    mapper.autoscale()
    assert string_similarity(old_image_array, mapper.widget.value) < 0.9

    # Update with larger range should make a new colorbar image
    artist.update(da * 3.1)
    mapper.autoscale()
    assert string_similarity(old_image_array, mapper.widget.value) < 0.9


def test_colorbar_does_not_update_if_no_autoscale():
    da = data_array(ndim=2, unit='K')
    mapper = ColorMapper()
    artist = DummyChild(data=da, colormapper=mapper)
    mapper.add_artist('data', artist)

    mapper.autoscale()
    _ = mapper.to_widget()
    old_image = mapper.widget.value
    old_image_array = old_image

    # Update with the same values
    artist.update(da)
    assert old_image is mapper.widget.value

    # Update with a smaller range
    artist.update(da * 0.8)
    assert old_image is mapper.widget.value

    # Update with larger range
    artist.update(da * 2.3)
    assert old_image_array is mapper.widget.value


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


def test_autoscale_vmin_set():
    da = data_array(ndim=2, unit='K')
    mapper = ColorMapper(vmin=-0.5)
    artist = DummyChild(data=da, colormapper=mapper)
    mapper.add_artist('data', artist)
    mapper.autoscale()
    assert mapper.vmin == -0.5
    assert mapper.vmax == da.max().value
    # Make sure it handles when da.max() is less than vmin
    artist.update(da - sc.scalar(5.0, unit='K'))
    mapper.autoscale()
    assert mapper.vmin == -0.5
    assert mapper.vmin < mapper.vmax


def test_autoscale_vmax_set():
    da = data_array(ndim=2, unit='K')
    mapper = ColorMapper(vmax=0.5)
    artist = DummyChild(data=da, colormapper=mapper)
    mapper.add_artist('data', artist)
    mapper.autoscale()
    assert mapper.vmax == 0.5
    assert mapper.vmin == da.min().value
    # Make sure it handles when da.min() is greater than vmax
    artist.update(da + sc.scalar(5.0, unit='K'))
    mapper.autoscale()
    assert mapper.vmax == 0.5
    assert mapper.vmin < mapper.vmax


CASES = {
    "imagefigure-mpl-static": (
        ('2d', 'mpl-static'),
        partial(imagefigure, cbar=True),
        partial(data_array, ndim=2),
    ),
    "imagefigure-mpl-interactive": (
        ('2d', 'mpl-interactive'),
        partial(imagefigure, cbar=True),
        partial(data_array, ndim=2),
    ),
    "scatter3dfigure-pythreejs": (
        ('3d', 'pythreejs'),
        partial(scatter3dfigure, x='x', y='y', z='z', cbar=True),
        scatter,
    ),
}


@pytest.mark.parametrize("backend,figure,data", CASES.values(), ids=CASES.keys())
class TestColormapperAllCases:
    def test_colorbar_label_has_name_with_one_artist(
        self, set_backend, backend, figure, data
    ):
        a = data(unit='K')
        a.name = 'A data'
        fig = figure(Node(a))
        assert fig.view.colormapper.ylabel == 'A data [K]'

    def test_colorbar_label_has_no_name_with_multiple_artists(
        self, set_backend, backend, figure, data
    ):
        a = data(unit='K')
        b = 3.3 * a
        a.name = 'A data'
        b.name = 'B data'
        fig = figure(Node(a), Node(b))
        assert fig.view.colormapper.ylabel == '[K]'


CASESINTERACTIVE = {k: c for k, c in CASES.items() if c[0][1] != 'mpl-static'}


@pytest.mark.parametrize(
    "backend,figure,data", CASESINTERACTIVE.values(), ids=CASESINTERACTIVE.keys()
)
class TestColormapperInteractiveCases:
    def test_toolbar_log_norm_button_state_agrees_with_kwarg(
        self, set_backend, backend, figure, data
    ):
        da = data()
        fig = figure(Node(da))
        assert not fig.toolbar['lognorm'].value
        assert fig.view.colormapper.norm == 'linear'
        fig = figure(Node(da), norm='log')
        assert fig.toolbar['lognorm'].value
        assert fig.view.colormapper.norm == 'log'

    def test_toolbar_log_norm_button_toggles_colormapper_norm(
        self, set_backend, backend, figure, data
    ):
        da = data()
        fig = figure(Node(da))
        assert fig.view.colormapper.norm == 'linear'
        fig.toolbar['lognorm'].value = True
        assert fig.view.colormapper.norm == 'log'
