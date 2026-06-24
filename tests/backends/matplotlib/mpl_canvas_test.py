# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026 Scipp contributors (https://github.com/scipp)

import matplotlib.pyplot as plt
import pytest

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

    canvas = da.plot(logx=False).canvas
    assert not canvas._logx_button.value
    assert not canvas._logy_button.value

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
    # Need to make buttons visible before we click them,
    # otherwise the contains() method returns False
    but.visible = True
    # Need to draw so that the contains() on the Text works
    canvas.fig.canvas.draw()

    # Convert axes coordinates to display coordinates
    x, y = canvas.ax.transAxes.transform(but.position)
    canvas._on_log_button_click(MouseEvent(x - 5, y - 5, None))
    assert canvas.xscale == 'log'
    assert but.value

    canvas._on_log_button_click(MouseEvent(x - 5, y - 5, None))
    assert canvas.xscale == 'linear'
    assert not but.value


@pytest.mark.parametrize("ndim", [1, 2])
def test_logy_button_state_agrees_with_kwarg(ndim):
    da = data_array(ndim=ndim)

    canvas = da.plot(logy=False).canvas
    assert not canvas._logy_button.value
    assert not canvas._logx_button.value

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
    # Need to make buttons visible before we click them,
    # otherwise the contains() method returns False
    but.visible = True
    # Need to draw so that the contains() on the Text works
    canvas.fig.canvas.draw()

    # Convert axes coordinates to display coordinates
    x, y = canvas.ax.transAxes.transform(but.position)
    canvas._on_log_button_click(MouseEvent(x - 5, y - 5, None))
    assert canvas.yscale == 'log'
    assert but.value

    canvas._on_log_button_click(MouseEvent(x - 5, y - 5, None))
    assert canvas.yscale == 'linear'
    assert not but.value


def test_logc_button_state_agrees_with_kwarg():
    da = data_array(ndim=2)
    canvas = da.plot(logc=True).canvas
    # Need to make a mouse move event to trigger the button update state, as it is
    # update only when mouse hovers over the cbar
    canvas.fig.canvas.draw()
    x, y = canvas.cax.transAxes.transform((0.5, 0.5))
    canvas._on_mouse_enter(None)
    assert canvas._logc_button.value


def test_logc_button_state_agrees_with_colormapper_norm():
    da = data_array(ndim=2)
    fig = da.plot()
    but = fig.canvas._logc_button
    assert not but.value
    assert fig.view.colormapper.norm == 'linear'
    fig.view.colormapper.norm = 'log'
    fig.canvas.fig.canvas.draw()
    x, y = fig.canvas.cax.transAxes.transform((0.5, 0.5))
    fig.canvas._on_mouse_enter(None)
    assert but.value


def test_clicking_logc_button_toggles_colormapper_norm():
    da = data_array(ndim=2)
    fig = da.plot()
    assert fig.view.colormapper.norm == 'linear'

    but = fig.canvas._logc_button
    but.visible = True
    fig.canvas.fig.canvas.draw()
    x, y = fig.canvas.cax.transAxes.transform(but.position)
    fig.canvas._on_log_button_click(MouseEvent(x, y - 5, fig.canvas.cax))
    assert fig.view.colormapper.norm == 'log'
    assert but.value

    fig.canvas._on_log_button_click(MouseEvent(x, y - 5, fig.canvas.cax))
    assert fig.view.colormapper.norm == 'linear'
    assert not but.value


def test_home_button_rescales_all_axes_sharing_a_figure():
    da = data_array(ndim=1)
    _, (ax0, ax1) = plt.subplots(2, 1)
    p0 = da.plot(ax=ax0)
    p1 = (da * 10.0).plot(ax=ax1)

    expected = p1.canvas.yrange
    # Perturb only the second figure.
    p1.canvas.yrange = (-100.0, 100.0)

    # Clicking Home on the first figure must also rescale the second one, since they
    # share the same Matplotlib figure (e.g. subplots).
    p0.toolbar['home'].callback()

    assert p1.canvas.yrange == pytest.approx(expected)
