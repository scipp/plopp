# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)
import pytest
import scipp as sc

from plopp import Node
from plopp.data.testing import data_array, scatter
from plopp.graphics import scatter3dfigure
from plopp.widgets import ClippingPlanes


@pytest.mark.parametrize('multiple_nodes', [False, True])
def test_add_remove_cuts(multiple_nodes):
    a = scatter()
    nodes = [Node(a)]
    if multiple_nodes:
        b = a.copy()
        b.coords['x'] += sc.scalar(60, unit='m')
        nodes.append(Node(b))

    fig = scatter3dfigure(*nodes, x='x', y='y', z='z', cbar=True)
    clip = ClippingPlanes(fig)
    assert len(fig.artists) == 1 * len(nodes)
    clip.add_x_cut.click()
    assert len(fig.artists) == 2 * len(nodes)
    npoints_in_cutx = list(fig.artists.values())[-1]._data.shape[0]
    clip.add_y_cut.click()
    assert len(fig.artists) == 2 * len(nodes)
    npoints_in_cutxy = list(fig.artists.values())[-1]._data.shape[0]
    assert npoints_in_cutxy > npoints_in_cutx
    clip.add_z_cut.click()
    assert len(fig.artists) == 2 * len(nodes)
    npoints_in_cutxyz = list(fig.artists.values())[-1]._data.shape[0]
    assert npoints_in_cutxyz > npoints_in_cutxy
    clip.delete_cut.click()
    # If the tool is not displayed, the tab selected index does not update when a cut
    # is deleted, so we need to manually set it to the correct value
    clip.tabs.selected_index = 1
    assert list(fig.artists.values())[-1]._data.shape[0] == npoints_in_cutxy
    clip.delete_cut.click()
    # If the tool is not displayed, the tab selected index does not update when a cut
    # is deleted, so we need to manually set it to the correct value
    clip.tabs.selected_index = 0
    assert list(fig.artists.values())[-1]._data.shape[0] == npoints_in_cutx
    clip.delete_cut.click()
    assert len(fig.artists) == 1 * len(nodes)


@pytest.mark.parametrize('multiple_nodes', [False, True])
def test_value_cuts(multiple_nodes):
    a = scatter()
    nodes = [Node(a)]
    if multiple_nodes:
        b = a.copy()
        b.coords['x'] += sc.scalar(60, unit='m')
        nodes.append(Node(b))
    fig = scatter3dfigure(*nodes, x='x', y='y', z='z', cbar=True)
    clip = ClippingPlanes(fig)
    clip.add_v_cut.click()
    vcut = clip.cuts[-1]
    npoints = list(fig.artists.values())[-1]._data.shape[0]
    vcut.slider.value = [vcut.slider.min, vcut.slider.value[1]]
    clip.update_state()  # Need to manually update state due to debounce mechanism
    # We should now have more points in the cut than before because the range is wider
    npoints2 = list(fig.artists.values())[-1]._data.shape[0]
    assert npoints2 > npoints

    clip.cut_operation.value = 'OR'
    # Add a second value cut
    clip.add_v_cut.click()
    vcut2 = clip.cuts[-1]
    vcut2.slider.value = [
        0.5 * (vcut2.slider.value[1] + vcut2.slider.max),
        vcut2.slider.max,
    ]
    clip.update_state()  # Need to manually update state due to debounce mechanism
    # We should now have more points in the cut than before because the range is wider
    npoints3 = list(fig.artists.values())[-1]._data.shape[0]
    assert npoints3 > npoints2

    clip.delete_cut.click()
    assert list(fig.artists.values())[-1]._data.shape[0] == npoints2
    # If the tool is not displayed, the tab selected index does not update when a cut
    # is deleted, so we need to manually set it to the correct value
    clip.tabs.selected_index = 0
    clip.delete_cut.click()
    assert len(fig.artists) == 1 * len(nodes)


def test_move_cut():
    da = scatter()
    fig = scatter3dfigure(Node(da), x='x', y='y', z='z', cbar=True)
    clip = ClippingPlanes(fig)
    clip.add_x_cut.click()
    xcut = clip.cuts[-1]
    assert xcut.outlines[0].position[0] == xcut.slider.value[0]
    assert xcut.outlines[1].position[0] == xcut.slider.value[1]
    pts = list(fig.artists.values())[-1]
    npoints = pts._data.shape[0]
    xcut.slider.value = [xcut.slider.min, xcut.slider.value[1]]
    assert xcut.outlines[0].position[0] == xcut.slider.value[0]
    assert xcut.outlines[1].position[0] == xcut.slider.value[1]
    clip.update_state()  # Need to manually update state due to debounce mechanism
    new_pts = list(fig.artists.values())[-1]
    assert npoints < new_pts._data.shape[0]


def test_operation_or():
    dim = 'pix'
    da = data_array(ndim=3).flatten(to=dim)
    fig = scatter3dfigure(Node(da), x='xx', y='yy', z='zz', cbar=True)
    clip = ClippingPlanes(fig)
    clip.cut_operation.value = 'OR'

    clip.add_x_cut.click()
    xcut = clip.cuts[-1]
    data_in_xcut = list(clip._nodes.values())[-1]['slice']()
    xrange = xcut.slider.value
    xsel = (da.coords['xx'] >= sc.scalar(xrange[0], unit='m')) & (
        da.coords['xx'] < sc.scalar(xrange[1], unit='m')
    )
    expected = da[xsel].flatten(to=dim)
    assert sc.identical(expected, data_in_xcut)

    clip.add_y_cut.click()
    ycut = clip.cuts[-1]
    data_in_xycut = list(clip._nodes.values())[-1]['slice']()
    yrange = ycut.slider.value
    ysel = (da.coords['yy'] >= sc.scalar(yrange[0], unit='m')) & (
        da.coords['yy'] < sc.scalar(yrange[1], unit='m')
    )
    expected = da[xsel | ysel].flatten(to=dim)
    assert sc.identical(expected, data_in_xycut)

    clip.add_z_cut.click()
    zcut = clip.cuts[-1]
    data_in_xyzcut = list(clip._nodes.values())[-1]['slice']()
    zrange = zcut.slider.value
    zsel = (da.coords['zz'] >= sc.scalar(zrange[0], unit='m')) & (
        da.coords['zz'] < sc.scalar(zrange[1], unit='m')
    )
    expected = da[xsel | ysel | zsel].flatten(to=dim)
    assert sc.identical(expected, data_in_xyzcut)


def test_operation_and():
    dim = 'pix'
    da = data_array(ndim=3).flatten(to=dim)
    fig = scatter3dfigure(Node(da), x='xx', y='yy', z='zz', cbar=True)
    clip = ClippingPlanes(fig)
    clip.cut_operation.value = 'AND'

    clip.add_x_cut.click()
    xcut = clip.cuts[-1]
    xrange = xcut.slider.value
    xsel = (da.coords['xx'] >= sc.scalar(xrange[0], unit='m')) & (
        da.coords['xx'] < sc.scalar(xrange[1], unit='m')
    )

    clip.add_y_cut.click()
    ycut = clip.cuts[-1]
    data_in_xycut = list(clip._nodes.values())[-1]['slice']()
    yrange = ycut.slider.value
    ysel = (da.coords['yy'] >= sc.scalar(yrange[0], unit='m')) & (
        da.coords['yy'] < sc.scalar(yrange[1], unit='m')
    )
    expected = da[xsel & ysel].flatten(to=dim)
    assert sc.identical(expected, data_in_xycut)

    clip.add_z_cut.click()
    zcut = clip.cuts[-1]
    data_in_xyzcut = list(clip._nodes.values())[-1]['slice']()
    zrange = zcut.slider.value
    zsel = (da.coords['zz'] >= sc.scalar(zrange[0], unit='m')) & (
        da.coords['zz'] < sc.scalar(zrange[1], unit='m')
    )
    expected = da[xsel & ysel & zsel].flatten(to=dim)
    assert sc.identical(expected, data_in_xyzcut)


def test_operation_xor():
    dim = 'pix'
    da = data_array(ndim=3).flatten(to=dim)
    fig = scatter3dfigure(Node(da), x='xx', y='yy', z='zz', cbar=True)
    clip = ClippingPlanes(fig)
    clip.cut_operation.value = 'XOR'

    clip.add_x_cut.click()
    xcut = clip.cuts[-1]
    xrange = xcut.slider.value
    xsel = (da.coords['xx'] >= sc.scalar(xrange[0], unit='m')) & (
        da.coords['xx'] < sc.scalar(xrange[1], unit='m')
    )

    clip.add_y_cut.click()
    ycut = clip.cuts[-1]
    data_in_xycut = list(clip._nodes.values())[-1]['slice']()
    yrange = ycut.slider.value
    ysel = (da.coords['yy'] >= sc.scalar(yrange[0], unit='m')) & (
        da.coords['yy'] < sc.scalar(yrange[1], unit='m')
    )
    expected = da[(xsel | ysel) & ~(xsel & ysel)].flatten(to=dim)
    assert sc.identical(expected, data_in_xycut)

    clip.add_z_cut.click()
    zcut = clip.cuts[-1]
    data_in_xyzcut = list(clip._nodes.values())[-1]['slice']()
    zrange = zcut.slider.value
    zsel = (da.coords['zz'] >= sc.scalar(zrange[0], unit='m')) & (
        da.coords['zz'] < sc.scalar(zrange[1], unit='m')
    )
    expected = da[
        (xsel | ysel | zsel) & ~(xsel & ysel) & ~(xsel & zsel) & ~(ysel & zsel)
    ].flatten(to=dim)
    assert sc.identical(expected, data_in_xyzcut)
