# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import matplotlib.pyplot as plt
import numpy as np
import pytest
import scipp as sc

import plopp as pp
from plopp.data.testing import data_array

pytestmark = pytest.mark.usefixtures("_parametrize_interactive_1d_backends")


class MouseEvent:
    def __init__(self, x, y, inaxes):
        self.x = x
        self.y = y
        self.inaxes = inaxes


@pytest.mark.parametrize("ndim", [1, 2])
def test_logx_button_state_agrees_with_kwarg(ndim):
    da = data_array(ndim=ndim)
    canvas = da.plot(logx=True).canvas
    assert canvas._logx_button.value
    assert not canvas._logy_button.value


@pytest.mark.parametrize("ndim", [1, 2])
def test_logx_button_state_agrees_with_xscale(ndim):
    da = data_array(ndim=ndim)
    canvas = da.plot().canvas
    but = canvas._logx_button
    assert not but.value
    assert canvas.xscale == 'linear'
    canvas.xscale = 'log'
    assert but.value


@pytest.mark.parametrize("ndim", [1, 2])
def test_clicking_logx_button_toggles_xscale(ndim):
    da = data_array(ndim=ndim)
    canvas = da.plot().canvas
    assert canvas.xscale == 'linear'

    but = canvas._logx_button
    # Convert axes coordinates to display coordinates
    x, y = canvas.ax.transAxes.transform(but.position)
    # Need to make buttons visible before we click them,
    # otherwise the contains() method returns False
    but.visible = True
    # Need to draw so that the contains() on the Text works
    canvas.fig.canvas.draw()
    canvas._on_log_button_click(MouseEvent(x - 5, y - 5, None))
    assert canvas.xscale == 'log'
    assert but.value

    canvas._on_log_button_click(MouseEvent(x - 5, y - 5, None))
    assert canvas.xscale == 'linear'
    assert not but.value


@pytest.mark.parametrize("ndim", [1, 2])
def test_logy_button_state_agrees_with_kwarg(ndim):
    da = data_array(ndim=ndim)
    canvas = da.plot(logy=True).canvas
    assert canvas._logy_button.value
    assert not canvas._logx_button.value


@pytest.mark.parametrize("ndim", [1, 2])
def test_logy_button_state_agrees_with_yscale(ndim):
    da = data_array(ndim=ndim)
    canvas = da.plot().canvas
    but = canvas._logy_button
    assert not but.value
    assert canvas.yscale == 'linear'
    canvas.yscale = 'log'
    assert but.value


@pytest.mark.parametrize("ndim", [1, 2])
def test_clicking_logy_button_toggles_yscale(ndim):
    da = data_array(ndim=ndim)
    canvas = da.plot().canvas
    assert canvas.yscale == 'linear'

    but = canvas._logy_button
    # Convert axes coordinates to display coordinates
    x, y = canvas.ax.transAxes.transform(but.position)
    # Need to make buttons visible before we click them,
    # otherwise the contains() method returns False
    but.visible = True
    # Need to draw so that the contains() on the Text works
    canvas.fig.canvas.draw()
    canvas._on_log_button_click(MouseEvent(x - 5, y - 5, None))
    assert canvas.yscale == 'log'
    assert but.value

    canvas._on_log_button_click(MouseEvent(x - 5, y - 5, None))
    assert canvas.yscale == 'linear'
    assert not but.value
