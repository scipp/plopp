# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Scipp contributors (https://github.com/scipp)
import pytest
import scipp as sc

import plopp as pp
from plopp.data import examples

CASES = {
    "line-mpl-static": (('2d', 'mpl-static'), pp.plot, (pp.data.data1d(),)),
    "line-mpl-interactive": (('2d', 'mpl-interactive'), pp.plot, (pp.data.data1d(),)),
    # The properties of plotly objects are not populated if the figure is not displayed
    # "line-plotly": (('2d', 'plotly'), pp.plot, (pp.data.data1d,)),
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
}


@pytest.mark.parametrize("backend,func,data", CASES.values(), ids=CASES.keys())
class TestArtists:
    def test_visible(self, set_backend, backend, func, data):
        fig = func(*data)
        [artist] = fig.artists.values()
        assert artist.visible
        artist.visible = False
        assert not artist.visible

    def opacity(self, set_backend, backend, func, data):
        fig = func(*data)
        [artist] = fig.artists.values()
        assert artist.opacity == 1.0
        artist.opacity = 0.5
        assert artist.opacity == 0.5
