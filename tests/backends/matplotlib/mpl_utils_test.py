# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import ipykernel.kernelapp
import pytest

from plopp.backends.matplotlib.canvas import Canvas
from plopp.backends.matplotlib.utils import subshells_in_use


class FakeSubshellManager:
    def __init__(self, subshells: list[str]):
        self._subshells = subshells

    def list_subshell(self) -> list[str]:
        return self._subshells


class FakeShellChannelThread:
    def __init__(self, subshells: list[str]):
        self.manager = FakeSubshellManager(subshells)


class FakeKernel:
    def __init__(self, supports_subshells: bool, subshells: list[str]):
        self._supports_kernel_subshells = supports_subshells
        self.shell_channel_thread = FakeShellChannelThread(subshells)


class FakeKernelApp:
    """Stub for ``IPKernelApp``, which is both a singleton and its own factory."""

    def __init__(self, kernel: object | None):
        self.kernel = kernel

    def initialized(self) -> bool:
        return self.kernel is not None

    def instance(self) -> 'FakeKernelApp':
        return self


@pytest.fixture
def fake_kernel_app(monkeypatch):
    def set_kernel(kernel: object | None):
        monkeypatch.setattr(
            ipykernel.kernelapp, 'IPKernelApp', FakeKernelApp(kernel=kernel)
        )

    return set_kernel


def test_subshells_in_use_no_kernel():
    assert not subshells_in_use()


def test_subshells_in_use_kernel_not_initialized(fake_kernel_app):
    fake_kernel_app(None)
    assert not subshells_in_use()


def test_subshells_in_use_kernel_without_subshell_support(fake_kernel_app):
    fake_kernel_app(FakeKernel(supports_subshells=False, subshells=[]))
    assert not subshells_in_use()


def test_subshells_in_use_no_subshells_created(fake_kernel_app):
    fake_kernel_app(FakeKernel(supports_subshells=True, subshells=[]))
    assert not subshells_in_use()


def test_subshells_in_use_with_subshells(fake_kernel_app):
    fake_kernel_app(FakeKernel(supports_subshells=True, subshells=['abcd-1234']))
    assert subshells_in_use()


def test_subshells_in_use_unexpected_kernel_api(fake_kernel_app):
    class KernelWithoutShellChannelThread:
        _supports_kernel_subshells = True

    fake_kernel_app(KernelWithoutShellChannelThread())
    assert not subshells_in_use()


def broken_canvas() -> Canvas:
    """Canvas whose layout fails, as it does when a subshell corrupts Matplotlib."""

    def tight_layout():
        raise ValueError('mathtext ParseException')

    canvas = Canvas()
    canvas.fig.tight_layout = tight_layout
    return canvas


@pytest.mark.usefixtures('_use_ipympl')
def test_to_widget_explains_concurrent_subshells(fake_kernel_app):
    fake_kernel_app(FakeKernel(supports_subshells=True, subshells=['abcd-1234']))
    with pytest.raises(RuntimeError, match='commsOverSubshells') as info:
        broken_canvas().to_widget()
    assert isinstance(info.value.__cause__, ValueError)


@pytest.mark.usefixtures('_use_ipympl')
def test_to_widget_reraises_when_no_subshells(fake_kernel_app):
    fake_kernel_app(FakeKernel(supports_subshells=True, subshells=[]))
    with pytest.raises(ValueError, match='mathtext ParseException'):
        broken_canvas().to_widget()
