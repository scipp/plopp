# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.data.testing import data_array
from plopp.functions.superplot import Superplot
import scipp as sc


def test_creation():
    da = data_array(ndim=2)
    sp = Superplot(da, keep='xx')
    assert len(sp.linesavetool._lines) == 0


def test_save_line():
    da = data_array(ndim=2)
    sp = Superplot(da, keep='xx')
    tool = sp.linesavetool
    assert len(tool._lines) == 0
    tool.save_line()
    assert len(tool._lines) == 1
    line = list(tool._lines.values())[-1]
    assert sc.identical(line['line']._data, da['yy', 0])
    assert len(tool.container.children) == 1

    sp.slider.controls['yy']['slider'].value = 5
    tool.save_line()
    assert len(tool._lines) == 2
    line = list(tool._lines.values())[-1]
    assert sc.identical(line['line']._data, da['yy', 5])
    assert len(tool.container.children) == 2


def test_remove_line():
    da = data_array(ndim=2)
    sp = Superplot(da, keep='xx')
    tool = sp.linesavetool
    assert len(tool._lines) == 0
    tool.save_line()
    sp.slider.controls['yy']['slider'].value = 5
    tool.save_line()
    sp.slider.controls['yy']['slider'].value = 15
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
    sp = Superplot(da, keep='xx')
    tool = sp.linesavetool
    tool.save_line()
    line_id = list(tool._lines.keys())[-1]
    tool.change_line_color(change={'new': '#000000'}, line_id=line_id)
    assert tool._lines[line_id]['line'].color == '#000000'
