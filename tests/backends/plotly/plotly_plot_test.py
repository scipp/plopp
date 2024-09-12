# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import matplotlib.pyplot as plt
import numpy as np
import pytest
import scipp as sc

import plopp as pp
from plopp.data.testing import data_array

pytest.importorskip("plotly")


def test_no_legend_for_single_artist():
    da = data_array(ndim=1)
    da.name = "Velocity"
    p = pp.plot(da)
    leg = p.ax.get_legend()
    assert leg is None


def test_legend_is_removed_when_only_one_artist_is_left():
    a = data_array(ndim=1)
    b = 2.3 * a
    f = pp.plot({'a': a, 'b': b})
    ka, _ = f.view.artists.keys()
    f.view.remove(ka)
    assert f.ax.get_legend() is None


def test_legend_entry_is_removed_when_artist_is_removed():
    a = data_array(ndim=1)
    b = 2.3 * a
    c = 0.8 * a
    f = pp.plot({'a': a, 'b': b, 'c': c})
    ka, _, _ = f.view.artists.keys()
    f.view.remove(ka)
    texts = f.ax.get_legend().get_texts()
    assert len(texts) == 2
    assert texts[0].get_text() == 'b'
    assert texts[1].get_text() == 'c'
