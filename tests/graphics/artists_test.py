# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Scipp contributors (https://github.com/scipp)

from functools import partial

import numpy as np
import pytest
import scipp as sc

import plopp as pp
from plopp.data import examples

CASES = {
    "line-mpl-static": (('2d', 'mpl-static'), pp.plot, {'obj': pp.data.data1d()}),
    "line-mpl-interactive": (
        ('2d', 'mpl-interactive'),
        pp.plot,
        {'obj': pp.data.data1d()},
    ),
    "line-mpl-masks-static": (
        ('2d', 'mpl-static'),
        pp.plot,
        {'obj': pp.data.data1d(masks=True)},
    ),
    "line-mpl-masks-interactive": (
        ('2d', 'mpl-interactive'),
        pp.plot,
        {'obj': pp.data.data1d(masks=True)},
    ),
    "line-mpl-errorbars-static": (
        ('2d', 'mpl-static'),
        pp.plot,
        {'obj': pp.data.data1d(variances=True)},
    ),
    "line-mpl-errorbars-interactive": (
        ('2d', 'mpl-interactive'),
        pp.plot,
        {'obj': pp.data.data1d(variances=True)},
    ),
    "image-mpl-static": (('2d', 'mpl-static'), pp.plot, {'obj': pp.data.data2d()}),
    "image-mpl-interactive": (
        ('2d', 'mpl-interactive'),
        pp.plot,
        {'obj': pp.data.data2d()},
    ),
    "scatter-mpl-static": (
        ('2d', 'mpl-static'),
        pp.scatter,
        {'obj': pp.data.scatter()},
    ),
    "scatter-mpl-interactive": (
        ('2d', 'mpl-interactive'),
        pp.scatter,
        {'obj': pp.data.scatter()},
    ),
    "scatter3d-pythreejs": (
        ('3d', 'pythreejs'),
        pp.scatter3d,
        {'obj': pp.data.scatter()},
    ),
    "mesh3d-pythreejs": (
        ('3d', 'pythreejs'),
        pp.mesh3d,
        dict(examples.teapot()),
    ),
    "mesh3d-pythreejs-edges": (
        ('3d', 'pythreejs'),
        partial(pp.mesh3d, edgecolor='blue'),
        dict(examples.teapot()),
    ),
}


@pytest.mark.parametrize(("backend", "func", "data"), CASES.values(), ids=CASES.keys())
class TestArtists:
    def test_visible(self, set_backend, backend, func, data):
        fig = func(**data)
        [artist] = fig.artists.values()
        assert artist.visible in (None, True)
        artist.visible = False
        assert not artist.visible

    def test_opacity(self, set_backend, backend, func, data):
        fig = func(**data)
        [artist] = fig.artists.values()
        assert artist.opacity in (None, 1.0)
        artist.opacity = 0.5
        assert artist.opacity == 0.5


LINE_CASES = {k: v for k, v in CASES.items() if k.startswith("line")}


@pytest.mark.parametrize(
    ("backend", "func", "data"), LINE_CASES.values(), ids=LINE_CASES.keys()
)
class TestLineBBox:
    def test_line_bbox(self, set_backend, backend, func, data):
        fig = func(**data)
        [artist] = fig.artists.values()
        bbox = artist.bbox(xscale='linear', yscale='linear')
        # Tolerance of 3 because there is padding around the line
        assert np.isclose(bbox.xmin, data['obj'].coords['x'].min().value, atol=3.0)
        assert np.isclose(bbox.xmax, data['obj'].coords['x'].max().value, atol=3.0)

        if data['obj'].variances is not None:
            ymin = (data['obj'] - sc.stddevs(data['obj'])).min()
        else:
            ymin = data['obj'].min()
        # Tolerance of 0.2 because there is padding below the line
        assert np.isclose(bbox.ymin, ymin.value, atol=0.2)

        if data['obj'].variances is not None:
            ymax = (data['obj'] + sc.stddevs(data['obj'])).max()
        else:
            ymax = data['obj'].max()
        # Tolerance of 0.2 because there is padding above the line
        assert np.isclose(bbox.ymax, ymax.value, atol=0.2)


LINE_BACKENDS = {k: v[0] for k, v in CASES.items() if k.startswith("line")}


@pytest.mark.parametrize(("backend"), LINE_BACKENDS.values(), ids=LINE_BACKENDS.keys())
class TestLineBBoxAllNan:
    def test_line_bbox_all_nan(self, set_backend, backend):
        a = pp.data.data1d()
        a.values[...] = np.nan
        fig = pp.plot(obj=a)
        [artist] = fig.artists.values()
        bbox = artist.bbox(xscale='linear', yscale='linear')
        assert bbox.xmin is not None
        assert bbox.xmax is not None
        assert bbox.ymin is None
        assert bbox.ymax is None
