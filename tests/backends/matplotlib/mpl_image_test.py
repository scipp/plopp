# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import scipp as sc

from plopp.backends.matplotlib.canvas import Canvas
from plopp.backends.matplotlib.image import Image
from plopp.data.testing import data_array


def test_image_creation():
    da = data_array(ndim=2)
    image = Image(canvas=Canvas(), data=da)
    assert sc.identical(image._data, da)


def test_image_creation_binedges():
    da = data_array(ndim=2, binedges=True)
    image = Image(canvas=Canvas(), data=da)
    assert sc.identical(image._data, da)


def test_image_creation_masks():
    da = data_array(ndim=2, masks=True)
    image = Image(canvas=Canvas(), data=da)
    assert sc.identical(image._data, da)


def test_image_creation_ragged_coord():
    da = data_array(ndim=2, ragged=True)
    image = Image(canvas=Canvas(), data=da)
    assert image._dim_2d == ('x', 'xx')
    assert image._dim_1d == ('y', 'yy')
    assert sc.identical(image._data, da)


def test_image_update():
    da = data_array(ndim=2)
    image = Image(canvas=Canvas(), data=da)
    assert sc.identical(image._data, da)
    image.update(da * 2.5)
    assert sc.identical(image._data, da * 2.5)
