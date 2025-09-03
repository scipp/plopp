# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import ipywidgets as ipw
import pytest

from plopp.widgets import HBar, VBar


@pytest.mark.parametrize('Bar', [VBar, HBar])
def test_bar_creation(Bar):
    b1 = ipw.Button(description='Button 1')
    b2 = ipw.Button(description='Button 2')
    bar = Bar([b1, b2])
    assert len(bar.children) == 2
    assert bar.children[0] is b1
    assert bar.children[1] is b2


@pytest.mark.parametrize('Bar', [VBar, HBar])
def test_bar_add(Bar):
    b1 = ipw.Button(description='Button 1')
    b2 = ipw.Button(description='Button 2')
    bar = Bar([b1])
    assert len(bar.children) == 1
    bar.add(b2)
    assert len(bar.children) == 2
    assert bar.children[0] is b1
    assert bar.children[1] is b2


@pytest.mark.parametrize('Bar', [VBar, HBar])
def test_bar_remove(Bar):
    b1 = ipw.Button(description='Button 1')
    b2 = ipw.Button(description='Button 2')
    bar = Bar([b1, b2])
    assert len(bar.children) == 2
    assert bar.children[0] is b1
    assert bar.children[1] is b2
    bar.remove(b1)
    assert len(bar.children) == 1
    assert bar.children[0] is b2
    bar = Bar([b1, b2])
    bar.remove(b2)
    assert len(bar.children) == 1
    assert bar.children[0] is b1


@pytest.mark.parametrize('Bar', [VBar, HBar])
def test_bar_indexing(Bar):
    b1 = ipw.Button(description='Button 1')
    b2 = ipw.Button(description='Button 2')
    bar = Bar([b1, b2])
    assert bar[0] is b1
    assert bar[1] is b2


@pytest.mark.parametrize('Bar', [VBar, HBar])
def test_bar_indexing_range(Bar):
    b1 = ipw.Button(description='Button 1')
    b2 = ipw.Button(description='Button 2')
    b3 = ipw.Button(description='Button 3')
    bar = Bar([b1, b2, b3])
    result = bar[1:3]
    assert isinstance(result, Bar)
    assert len(result.children) == 2
    assert result.children[0] is b2
    assert result.children[1] is b3


@pytest.mark.parametrize('Bar', [VBar, HBar])
def test_bar_indexing_range_step(Bar):
    b1 = ipw.Button(description='Button 1')
    b2 = ipw.Button(description='Button 2')
    b3 = ipw.Button(description='Button 3')
    bar = Bar([b1, b2, b3])
    result = bar[0:3:2]
    assert isinstance(result, Bar)
    assert len(result.children) == 2
    assert result.children[0] is b1
    assert result.children[1] is b3


@pytest.mark.parametrize('Bar', [VBar, HBar])
def test_bar_length(Bar):
    b1 = ipw.Button(description='Button 1')
    b2 = ipw.Button(description='Button 2')
    b3 = ipw.Button(description='Button 3')
    bar = Bar([b1, b2, b3])
    assert len(bar) == 3
