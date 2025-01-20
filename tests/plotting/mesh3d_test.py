# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

import numpy as np
import pytest
import scipp as sc

import plopp as pp
from plopp.data import examples


@pytest.fixture
def teapot_data():
    return sc.io.load_hdf5(examples.teapot())


def test_mesh3d_default(teapot_data):
    pp.mesh3d(
        vertices=teapot_data["vertices"],
        faces=teapot_data["faces"],
    )


def test_mesh3d_solid_color(teapot_data):
    fig = pp.mesh3d(
        vertices=teapot_data["vertices"], faces=teapot_data["faces"], color='red'
    )
    (mesh,) = fig.artists.values()
    assert np.array_equal(mesh.geometry.attributes["color"].array[0, :], (1, 0, 0))


def test_mesh3d_vertexcolors(teapot_data):
    z = teapot_data["vertices"].fields.z
    fig = pp.mesh3d(
        vertices=teapot_data["vertices"],
        faces=teapot_data["faces"],
        vertexcolors=z,
    )
    assert fig.view.colormapper is not None
    (mesh,) = fig.artists.values()
    colors = mesh.geometry.attributes["color"].array
    imin = np.argmin(z.values)
    imax = np.argmax(z.values)
    assert not np.array_equal(colors[imin, :], colors[imax, :])


def test_mesh3d_edgecolor(teapot_data):
    fig = pp.mesh3d(
        vertices=teapot_data["vertices"],
        faces=teapot_data["faces"],
        vertexcolors=teapot_data["vertices"].fields.z,
        edgecolor='blue',
    )
    (mesh,) = fig.artists.values()
    assert mesh.edges.material.color == 'blue'


def test_mesh3d_cmap(teapot_data):
    fig = pp.mesh3d(
        vertices=teapot_data["vertices"],
        faces=teapot_data["faces"],
        vertexcolors=teapot_data["vertices"].fields.z,
        cmap='magma',
    )
    assert fig.view.colormapper.cmap.name == 'magma'
