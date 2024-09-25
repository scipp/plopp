# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)
import pytest
import scipp as sc

from plopp import Node
from plopp.data.testing import data_array
from plopp.plotting.superplot import superplot

pytestmark = pytest.mark.usefixtures("_parametrize_interactive_1d_backends")


def test_creation():
    da = data_array(ndim=2)
    sp = superplot(da, keep='xx')
    assert len(sp.right_bar[0]._lines) == 0


def test_from_node():
    da = data_array(ndim=2)
    superplot(Node(da))


def test_save_line():
    da = data_array(ndim=2)
    sp = superplot(da, keep='xx')
    tool = sp.right_bar[0]
    assert len(tool._lines) == 0
    tool.save_line()
    assert len(tool._lines) == 1
    line = list(tool._lines.values())[-1]
    assert sc.identical(line['line']._data, da['yy', 0])
    assert len(tool.container.children) == 1

    slider = sp.bottom_bar[0]
    slider.controls['yy']['slider'].value = 5
    tool.save_line()
    assert len(tool._lines) == 2
    line = list(tool._lines.values())[-1]
    assert sc.identical(line['line']._data, da['yy', 5])
    assert len(tool.container.children) == 2


def test_remove_line():
    da = data_array(ndim=2)
    sp = superplot(da, keep='xx')
    tool = sp.right_bar[0]
    assert len(tool._lines) == 0
    tool.save_line()
    slider = sp.bottom_bar[0]
    slider.controls['yy']['slider'].value = 5
    tool.save_line()
    slider.controls['yy']['slider'].value = 15
    tool.save_line()
    assert len(tool._lines) == 3
    assert len(tool.container.children) == 3

    keys = list(tool._lines.keys())
    first_line = keys[0]
    last_line = keys[2]

    tool.remove_line(change=None, line_id=first_line)
    assert first_line not in tool._lines
    assert len(tool.container.children) == 2

    tool.remove_line(change=None, line_id=last_line)
    assert last_line not in tool._lines
    assert len(tool.container.children) == 1


def test_change_line_color():
    da = data_array(ndim=2)
    sp = superplot(da, keep='xx')
    tool = sp.right_bar[0]
    tool.save_line()
    line_id = list(tool._lines.keys())[-1]
    tool.change_line_color(change={'new': '#000000'}, line_id=line_id)
    assert tool._lines[line_id]['line'].color == '#000000'


def test_raises_ValueError_when_given_binned_data():
    da = sc.data.table_xyz(100).bin(x=10, y=20)
    with pytest.raises(ValueError, match='Cannot plot binned data'):
        superplot(da, keep='x')
