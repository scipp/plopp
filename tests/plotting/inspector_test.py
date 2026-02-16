# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)
import pytest
import scipp as sc

import plopp as pp


@pytest.mark.usefixtures('_use_ipympl')
def test_creation():
    da = pp.data.data3d()
    pp.inspector(da)


@pytest.mark.usefixtures('_use_ipympl')
def test_from_node():
    da = pp.data.data3d()
    pp.inspector(pp.Node(da))


@pytest.mark.usefixtures('_use_ipympl')
def test_multiple_inputs_raises():
    da = pp.data.data3d()
    with pytest.raises(TypeError, match='Cannot convert input of type'):
        pp.inspector({'a': da, 'b': 2.3 * da})


@pytest.mark.usefixtures('_use_ipympl')
def test_bad_number_of_dims_raises():
    with pytest.raises(
        ValueError,
        match='The inspector plot currently only works with three-dimensional data',
    ):
        pp.inspector(pp.data.data2d())
    with pytest.raises(
        ValueError,
        match='The inspector plot currently only works with three-dimensional data',
    ):
        pp.inspector(pp.data.data_array(ndim=4))


@pytest.mark.usefixtures('_use_ipympl')
def test_raises_ValueError_when_given_binned_data():
    da = sc.data.table_xyz(100).bin(x=10, y=20, z=30)
    with pytest.raises(ValueError, match='Cannot plot binned data'):
        pp.inspector(da, orientation='vertical')


@pytest.mark.usefixtures('_use_ipympl')
def test_line_creation():
    da = pp.data.data3d()
    ip = pp.inspector(da)
    fig2d = ip[0][0]
    fig1d = ip[0][1]
    # Activate the inspector tool
    fig2d.toolbar['inspect'].value = True
    assert not fig1d.canvas.dims
    assert len(fig1d.artists) == 0
    fig2d.toolbar['inspect']._tool.click(10, 10)
    assert fig1d.canvas.dims == {'x': da.dims[-1]}
    assert len(fig1d.artists) == 1
    fig2d.toolbar['inspect']._tool.click(20, 15)
    assert len(fig1d.artists) == 2


@pytest.mark.usefixtures('_use_ipympl')
def test_line_removal():
    da = pp.data.data3d()
    ip = pp.inspector(da)
    fig2d = ip[0][0]
    fig1d = ip[0][1]
    fig2d.toolbar['inspect'].value = True
    assert not fig1d.canvas.dims
    assert len(fig1d.artists) == 0
    fig2d.toolbar['inspect']._tool.click(10, 10)
    assert fig1d.canvas.dims == {'x': da.dims[-1]}
    assert len(fig1d.artists) == 1
    fig2d.toolbar['inspect']._tool.click(20, 15)
    assert len(fig1d.artists) == 2
    fig2d.toolbar['inspect']._tool.remove(1)
    assert len(fig1d.artists) == 1
    fig2d.toolbar['inspect']._tool.remove(0)
    assert len(fig1d.artists) == 0


@pytest.mark.usefixtures('_use_ipympl')
def test_kwargs_propagation():
    da = pp.data.data3d()
    ip = pp.inspector(da, xmin=2, xmax=8, ymin=-0.25, ymax=0.75, norm="log")
    fig2d = ip[0][0]
    fig1d = ip[0][1]
    # Activate the inspector tool
    fig2d.toolbar['inspect'].value = True
    assert not fig1d.canvas.dims
    fig2d.toolbar['inspect']._tool.click(10, 10)

    # Controlling limits get sent to the 1D figure
    assert fig1d.canvas.xrange == (2, 8)
    assert fig1d.canvas.yrange == (-0.25, 0.75)
    assert fig2d.canvas.xrange != (2, 8)
    assert fig2d.canvas.yrange != (-0.25, 0.75)

    # Log norm is applied to the 2D figure
    assert fig1d.canvas.yscale == "linear"
    assert fig2d.view.colormapper.norm == "log"


@pytest.mark.usefixtures('_use_ipympl')
def test_polygon_mode_triangle():
    da = sc.DataArray(
        data=sc.array(
            dims=["xx", "yy", "zz"],
            values=[
                [[0, 1, 2], [3, 4, 5], [6, 7, 8]],
                [[9, 10, 11], [12, 13, 14], [15, 16, 17]],
                [[18, 19, 20], [21, 22, 23], [24, 25, 26]],
                [[27, 28, 29], [30, 31, 32], [33, 34, 35]],
            ],
        ),
        coords={
            "xx": sc.array(
                dims=['xx'], values=[0.0, 100.0, 200.0, 300.0, 400.0], unit='m'
            ),
            "yy": sc.array(dims=['yy'], values=[0.0, 10.0, 20.0, 30.0], unit='m'),
            "zz": sc.array(dims=['zz'], values=[0.0, 1.0, 2.0], unit='m'),
        },
    )

    ip = pp.inspector(da, mode='polygon', dim='zz')
    fig2d = ip[0][0]
    fig1d = ip[0][1]
    fig2d.toolbar['inspect'].value = True
    tool = fig2d.toolbar['inspect']._tool

    # This triangle should select the bottom left corner of the data.
    # Closing the polygon by repeating the first point.
    x = [-1, 32, -1, -1]
    y = [-1, -1, 350, -1]
    for xi, yi in zip(x, y, strict=True):
        tool.click(x=xi, y=yi)

    mask = sc.array(
        dims=['xx', 'yy'],
        values=[
            [False, False, False],
            [False, False, True],
            [False, True, True],
            [True, True, True],
        ],
    )

    expected = da.assign_masks(m=mask).sum(["xx", "yy"])
    line = next(iter(fig1d.artists.values()))
    assert sc.identical(line._data, expected)


@pytest.mark.usefixtures('_use_ipympl')
def test_polygon_mode_square():
    da = sc.DataArray(
        data=sc.array(
            dims=["xx", "yy", "zz"],
            values=[
                [[0, 1, 2], [3, 4, 5], [6, 7, 8]],
                [[9, 10, 11], [12, 13, 14], [15, 16, 17]],
                [[18, 19, 20], [21, 22, 23], [24, 25, 26]],
                [[27, 28, 29], [30, 31, 32], [33, 34, 35]],
            ],
        ),
        coords={
            "xx": sc.array(
                dims=['xx'], values=[0.0, 100.0, 200.0, 300.0, 400.0], unit='m'
            ),
            "yy": sc.array(dims=['yy'], values=[0.0, 10.0, 20.0, 30.0], unit='m'),
            "zz": sc.array(dims=['zz'], values=[0.0, 1.0, 2.0], unit='m'),
        },
    )

    ip = pp.inspector(da, mode='polygon', dim='zz')
    fig2d = ip[0][0]
    fig1d = ip[0][1]
    fig2d.toolbar['inspect'].value = True
    tool = fig2d.toolbar['inspect']._tool

    # This square should select the top right corner of the data.
    x = [11, 32, 32, 11, 11]
    y = [101, 101, 410, 410, 101]
    for xi, yi in zip(x, y, strict=True):
        tool.click(x=xi, y=yi)

    mask = sc.array(
        dims=['xx', 'yy'],
        values=[
            [True, True, True],
            [True, False, False],
            [True, False, False],
            [True, False, False],
        ],
    )

    expected = da.assign_masks(m=mask).sum(["xx", "yy"])
    line = next(iter(fig1d.artists.values()))
    assert sc.identical(line._data, expected)


@pytest.mark.usefixtures('_use_ipympl')
def test_polygon_mode_triangle_with_mask_in_third_dimension():
    da = sc.DataArray(
        data=sc.array(
            dims=["xx", "yy", "zz"],
            values=[
                [[0, 1, 2], [3, 4, 5], [6, 7, 8]],
                [[9, 10, 11], [12, 13, 14], [15, 16, 17]],
                [[18, 19, 20], [21, 22, 23], [24, 25, 26]],
                [[27, 28, 29], [30, 31, 32], [33, 34, 35]],
            ],
        ),
        coords={
            "xx": sc.array(
                dims=['xx'], values=[0.0, 100.0, 200.0, 300.0, 400.0], unit='m'
            ),
            "yy": sc.array(dims=['yy'], values=[0.0, 10.0, 20.0, 30.0], unit='m'),
            "zz": sc.array(dims=['zz'], values=[0.0, 1.0, 2.0], unit='m'),
        },
        masks={'mask': sc.array(dims=['zz'], values=[False, True, False])},
    )

    ip = pp.inspector(da, mode='polygon', dim='zz')
    fig2d = ip[0][0]
    fig1d = ip[0][1]
    fig2d.toolbar['inspect'].value = True
    tool = fig2d.toolbar['inspect']._tool

    # This triangle should select the bottom left corner of the data.
    # Closing the polygon by repeating the first point.
    x = [-1, 32, -1, -1]
    y = [-1, -1, 350, -1]
    for xi, yi in zip(x, y, strict=True):
        tool.click(x=xi, y=yi)

    mask = sc.array(
        dims=['xx', 'yy'],
        values=[
            [False, False, False],
            [False, False, True],
            [False, True, True],
            [True, True, True],
        ],
    )

    expected = da.assign_masks(m=mask).sum(["xx", "yy"])
    line = next(iter(fig1d.artists.values()))
    assert sc.identical(line._data, expected)


@pytest.mark.usefixtures('_use_ipympl')
def test_polygon_mode_preserves_keep_dim_binedges():
    da = sc.DataArray(
        data=sc.array(
            dims=["xx", "yy", "zz"],
            values=[
                [[0, 1, 2], [3, 4, 5], [6, 7, 8]],
                [[9, 10, 11], [12, 13, 14], [15, 16, 17]],
                [[18, 19, 20], [21, 22, 23], [24, 25, 26]],
                [[27, 28, 29], [30, 31, 32], [33, 34, 35]],
            ],
        ),
        coords={
            "xx": sc.array(
                dims=['xx'], values=[0.0, 100.0, 200.0, 300.0, 400.0], unit='m'
            ),
            "yy": sc.array(dims=['yy'], values=[0.0, 10.0, 20.0, 30.0], unit='m'),
            "zz": sc.array(dims=['zz'], values=[0.0, 1.0, 2.0, 3.0], unit='m'),
        },
    )

    ip = pp.inspector(da, mode='polygon', dim='zz')
    fig2d = ip[0][0]
    fig1d = ip[0][1]
    fig2d.toolbar['inspect'].value = True
    tool = fig2d.toolbar['inspect']._tool

    # This triangle should select the bottom left corner of the data.
    # Closing the polygon by repeating the first point.
    x = [-1, 32, -1, -1]
    y = [-1, -1, 350, -1]
    for xi, yi in zip(x, y, strict=True):
        tool.click(x=xi, y=yi)

    mask = sc.array(
        dims=['xx', 'yy'],
        values=[
            [False, False, False],
            [False, False, True],
            [False, True, True],
            [True, True, True],
        ],
    )

    expected = da.assign_masks(m=mask).sum(["xx", "yy"])
    line = next(iter(fig1d.artists.values()))
    assert sc.identical(line._data, expected)
    assert line._data.coords.is_edges("zz", dim="zz")
