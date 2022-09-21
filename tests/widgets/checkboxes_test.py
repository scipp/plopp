# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.widgets import Checkboxes


def test_checkboxes_creation():
    desc = 'My Checkboxes'
    cbx = Checkboxes(['a', 'b', 'c'], description=desc)
    assert 'a' in cbx.checkboxes
    assert 'b' in cbx.checkboxes
    assert 'c' in cbx.checkboxes
    assert cbx.description.value == desc
    assert cbx.checkboxes['a'].value
    assert cbx.checkboxes['b'].value
    assert cbx.checkboxes['c'].value
    assert cbx.toggle_all_button.value


def test_checkboxes_initial_value():
    cbx = Checkboxes(['a', 'b', 'c'], value=False)
    assert not cbx.checkboxes['a'].value
    assert not cbx.checkboxes['b'].value
    assert not cbx.checkboxes['c'].value
    assert not cbx.toggle_all_button.value


def test_checkboxes_value_property():
    cbx = Checkboxes(['a', 'b', 'c'])
    cbx.checkboxes['b'].value = False
    assert cbx.value == {'a': True, 'b': False, 'c': True}
