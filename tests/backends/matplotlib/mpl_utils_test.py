# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import matplotlib
import pytest

from plopp.backends.matplotlib.figure import MplFigure
from plopp.backends.matplotlib.utils import is_interactive_backend, is_widget_backend
from plopp.data.testing import data_array


@pytest.mark.parametrize(
    'backend', ['qtagg', 'tkagg', 'macosx', 'gtk4agg', 'wxagg', 'webagg']
)
def test_gui_backends_are_interactive_but_not_widget(monkeypatch, backend):
    monkeypatch.setattr(matplotlib, 'get_backend', lambda: backend)
    assert is_interactive_backend()
    assert not is_widget_backend()


@pytest.mark.parametrize('backend', ['module://ipympl.backend_nbagg', 'nbagg'])
def test_widget_backends_are_interactive_and_widget(monkeypatch, backend):
    monkeypatch.setattr(matplotlib, 'get_backend', lambda: backend)
    assert is_interactive_backend()
    assert is_widget_backend()


@pytest.mark.parametrize(
    'backend', ['agg', 'module://matplotlib_inline.backend_inline', 'pdf', 'svg']
)
def test_static_backends_are_neither_interactive_nor_widget(monkeypatch, backend):
    monkeypatch.setattr(matplotlib, 'get_backend', lambda: backend)
    assert not is_interactive_backend()
    assert not is_widget_backend()


@pytest.mark.parametrize('backend', ['qtagg', 'tkagg', 'macosx'])
def test_gui_backend_makes_default_figure(monkeypatch, backend):
    # GUI backends are used when plotting from a terminal, where ipywidgets-based
    # interactive figures cannot be displayed. See issue #589.
    monkeypatch.setattr(matplotlib, 'get_backend', lambda: backend)
    fig = data_array(ndim=1).plot()

    assert isinstance(fig, MplFigure)
    assert not fig.interactive
