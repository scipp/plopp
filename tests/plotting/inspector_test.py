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


def _finalize_polygon(tool, points):
    """
    Click the polygon vertices and force creation without needing a close gesture.
    """
    for x, y in points:
        tool.click(x, y)
    # Finalize to trigger the on_create callback without needing to close the polygon.
    tool._finalize_owner()


def _coord_margin(values, index):
    """
    Return a small margin around a coordinate to build a polygon around a bin center.
    """
    if index == 0:
        return (values[1] - values[0]) / 4.0
    if index == len(values) - 1:
        return (values[-1] - values[-2]) / 4.0
    return (
        min(values[index] - values[index - 1], values[index + 1] - values[index]) / 4.0
    )


def _polygon_vertices(da, xdim, ydim, x_index, y_indices):
    """
    Build a rectangle polygon around the given x index and y index range.
    """
    xvalues = da.coords[xdim].values
    yvalues = da.coords[ydim].values
    y_start = y_indices[0]
    y_end = y_indices[-1]
    x0 = xvalues[x_index]
    y0 = yvalues[y_start]
    y1 = yvalues[y_end]
    x_margin = _coord_margin(xvalues, x_index)
    y_margin_start = _coord_margin(yvalues, y_start)
    y_margin_end = _coord_margin(yvalues, y_end)
    return [
        (x0 - x_margin, y0 - y_margin_start),
        (x0 + x_margin, y0 - y_margin_start),
        (x0 + x_margin, y1 + y_margin_end),
        (x0 - x_margin, y1 + y_margin_end),
    ]


def _polygon_case(
    *,
    dims,
    values,
    coords,
    x_index,
    y_indices,
    keep_dim=None,
):
    """
    Create a polygon test case with input data and the selection indices to compare.
    """
    return (
        sc.DataArray(
            data=sc.array(dims=dims, values=values),
            coords={
                name: sc.array(dims=[name], values=vals)
                for name, vals in coords.items()
            },
        ),
        x_index,
        y_indices,
        keep_dim,
    )


@pytest.mark.usefixtures('_use_ipympl')
@pytest.mark.parametrize(
    ("da", "x_index", "y_indices", "keep_dim"),
    [
        _polygon_case(
            dims=["yy", "xx", "zz"],
            values=[
                [[0, 1], [2, 3], [4, 5]],
                [[6, 7], [8, 9], [10, 11]],
                [[12, 13], [14, 15], [16, 17]],
            ],
            coords={
                "yy": [0.0, 10.0, 20.0],
                "xx": [0.0, 5.0, 10.0],
                "zz": [1.0, 2.0],
            },
            x_index=1,
            y_indices=[1],
            keep_dim=None,
        ),
        _polygon_case(
            dims=["row", "depth", "col"],
            values=[
                [[0, 1, 2], [3, 4, 5], [6, 7, 8]],
                [[9, 10, 11], [12, 13, 14], [15, 16, 17]],
                [[18, 19, 20], [21, 22, 23], [24, 25, 26]],
                [[27, 28, 29], [30, 31, 32], [33, 34, 35]],
            ],
            coords={
                "row": [0.0, 100.0, 200.0, 300.0],
                "col": [0.0, 10.0, 20.0],
                "depth": [0.0, 1.0, 2.0],
            },
            x_index=1,
            y_indices=[1, 2],
            keep_dim="row",
        ),
    ],
)
def test_polygon_mode_data_values(da, x_index, y_indices, keep_dim):
    """
    Polygon selection should produce the expected 1D curve over the keep dimension.
    """
    if keep_dim is None:
        keep_dim = da.dims[-1]
    ip = pp.inspector(da, mode='polygon', dim=keep_dim)
    fig2d = ip[0][0]
    fig1d = ip[0][1]
    fig2d.toolbar['inspect'].value = True
    tool = fig2d.toolbar['inspect']._tool
    xdim = fig2d.canvas.dims['x']
    ydim = fig2d.canvas.dims['y']
    keep_dim = keep_dim
    points = _polygon_vertices(da, xdim, ydim, x_index=x_index, y_indices=y_indices)
    _finalize_polygon(tool, points)
    assert fig1d.canvas.dims == {'x': keep_dim}
    assert len(fig1d.artists) == 1
    line = next(iter(fig1d.artists.values()))
    if len(y_indices) == 1:
        expected = da[ydim, y_indices[0]][xdim, x_index]
    else:
        expected = da[ydim, y_indices][xdim, x_index].sum(ydim)
    expected = expected.drop_coords(
        [name for name in expected.coords if name != keep_dim]
    )
    assert sc.identical(line._data, expected)


@pytest.mark.usefixtures('_use_ipympl')
def test_polygon_mode_respects_masks_on_keep_dim():
    """
    Masks on the keep dimension should propagate to the 1D output.
    """
    da = sc.DataArray(
        data=sc.array(
            dims=["yy", "xx", "zz"],
            values=[
                [[0.0, 1.0, 2.0], [3.0, 4.0, 5.0]],
                [[6.0, 7.0, 8.0], [9.0, 10.0, 11.0]],
            ],
        ),
        coords={
            "yy": sc.array(dims=["yy"], values=[0.0, 1.0]),
            "xx": sc.array(dims=["xx"], values=[0.0, 1.0]),
            "zz": sc.array(dims=["zz"], values=[0.0, 1.0, 2.0]),
        },
        masks={
            "masked": sc.array(dims=["zz"], values=[False, True, False]),
        },
    )
    ip = pp.inspector(da, mode="polygon")
    fig2d = ip[0][0]
    fig1d = ip[0][1]
    fig2d.toolbar["inspect"].value = True
    tool = fig2d.toolbar["inspect"]._tool
    xdim = fig2d.canvas.dims["x"]
    ydim = fig2d.canvas.dims["y"]
    points = _polygon_vertices(da, xdim, ydim, x_index=0, y_indices=[0, 1])
    _finalize_polygon(tool, points)
    line = next(iter(fig1d.artists.values()))
    expected = da[ydim, [0, 1]][xdim, 0].sum(ydim)
    expected = expected.drop_coords(
        [name for name in expected.coords if name != da.dims[-1]]
    )
    assert sc.identical(line._data, expected)
    assert "masked" in line._data.masks


@pytest.mark.usefixtures('_use_ipympl')
def test_polygon_mode_preserves_keep_dim_binedges():
    """
    Bin-edge coordinates on the keep dimension should be preserved in the 1D output.
    """
    da = sc.DataArray(
        data=sc.array(
            dims=["yy", "xx", "zz"],
            values=[
                [[0.0, 1.0], [2.0, 3.0]],
                [[4.0, 5.0], [6.0, 7.0]],
            ],
        ),
        coords={
            "yy": sc.array(dims=["yy"], values=[0.0, 1.0]),
            "xx": sc.array(dims=["xx"], values=[0.0, 1.0]),
            "zz": sc.array(dims=["zz"], values=[0.0, 1.0, 2.0]),
        },
    )
    assert da.coords.is_edges("zz", dim="zz")
    ip = pp.inspector(da, mode="polygon")
    fig2d = ip[0][0]
    fig1d = ip[0][1]
    fig2d.toolbar["inspect"].value = True
    tool = fig2d.toolbar["inspect"]._tool
    xdim = fig2d.canvas.dims["x"]
    ydim = fig2d.canvas.dims["y"]
    points = _polygon_vertices(da, xdim, ydim, x_index=1, y_indices=[0, 1])
    _finalize_polygon(tool, points)
    line = next(iter(fig1d.artists.values()))
    assert line._data.coords.is_edges("zz", dim="zz")


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
