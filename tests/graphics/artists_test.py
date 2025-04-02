# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Scipp contributors (https://github.com/scipp)

from functools import partial

import pytest
import scipp as sc

import plopp as pp
from plopp.data import examples

CASES = {
    "line-mpl-static": (('2d', 'mpl-static'), pp.plot, (pp.data.data1d(),)),
    "line-mpl-interactive": (('2d', 'mpl-interactive'), pp.plot, (pp.data.data1d(),)),
    "line-mpl-masks-static": (
        ('2d', 'mpl-static'),
        pp.plot,
        (pp.data.data1d(masks=True),),
    ),
    "line-mpl-masks-interactive": (
        ('2d', 'mpl-interactive'),
        pp.plot,
        (pp.data.data1d(masks=True),),
    ),
    "line-mpl-errorbars-static": (
        ('2d', 'mpl-static'),
        pp.plot,
        (pp.data.data1d(variances=True),),
    ),
    "line-mpl-errorbars-interactive": (
        ('2d', 'mpl-interactive'),
        pp.plot,
        (pp.data.data1d(variances=True),),
    ),
    "line-plotly": (('2d', 'plotly'), pp.plot, (pp.data.data1d,)),
    "line-plotly-masks": (('2d', 'plotly'), pp.plot, (pp.data.data1d(masks=True),)),
    "line-plotly-errorbars": (
        ('2d', 'plotly'),
        pp.plot,
        (pp.data.data1d(variances=True),),
    ),
    "image-mpl-static": (('2d', 'mpl-static'), pp.plot, (pp.data.data2d(),)),
    "image-mpl-interactive": (('2d', 'mpl-interactive'), pp.plot, (pp.data.data2d(),)),
    "scatter-mpl-static": (('2d', 'mpl-static'), pp.scatter, (pp.data.scatter(),)),
    "scatter-mpl-interactive": (
        ('2d', 'mpl-interactive'),
        pp.scatter,
        (pp.data.scatter(),),
    ),
    "scatter3d-pythreejs": (('3d', 'pythreejs'), pp.scatter3d, (pp.data.scatter(),)),
    "mesh3d-pythreejs": (
        ('3d', 'pythreejs'),
        pp.mesh3d,
        list(sc.io.load_hdf5(examples.teapot()).values()),
    ),
    "mesh3d-pythreejs-edges": (
        ('3d', 'pythreejs'),
        partial(pp.mesh3d, edgecolor='blue'),
        list(sc.io.load_hdf5(examples.teapot()).values()),
    ),
}


@pytest.mark.parametrize("backend,func,data", CASES.values(), ids=CASES.keys())
class TestArtists:
    def test_visible(self, set_backend, backend, func, data):
        fig = func(*data)
        [artist] = fig.artists.values()
        assert artist.visible in (None, True)
        artist.visible = False
        assert not artist.visible

    def test_opacity(self, set_backend, backend, func, data):
        fig = func(*data)
        [artist] = fig.artists.values()
        assert artist.opacity in (None, 1.0)
        artist.opacity = 0.5
        assert artist.opacity == 0.5
