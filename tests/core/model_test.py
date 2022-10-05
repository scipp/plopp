# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp import Node, node, View
from functools import partial
import pytest


class SimpleView(View):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = None

    def notify_view(self, message):
        self.value = message


def test_two_nodes_parent_child():
    a = Node(lambda: 5)
    b = node(lambda x: x - 2)(x=a)
    assert 'x' in b.kwparents
    assert a is b.kwparents['x']
    assert b in a.children


def test_two_nodes_notify_children():
    a = Node(lambda: 5)
    b = node(lambda x: x - 2)(x=a)
    av = SimpleView(a)
    bv = SimpleView(b)
    assert av in a.views
    assert bv in b.views

    msg = 'hello from b'
    b.notify_children(message=msg)
    assert av.value is None
    assert 'node_id' in bv.value
    assert bv.value['message'] == msg

    msg = 'hello from a'
    a.notify_children(message=msg)
    assert 'node_id' in av.value
    assert av.value['message'] == msg
    assert 'node_id' in bv.value
    assert bv.value['message'] == msg


def test_two_children_notify_children():
    a = Node(lambda: 5)
    b = node(lambda x: x - 2)(x=a)
    c = node(lambda x: x + 2)(x=a)
    av = SimpleView(a)
    bv = SimpleView(b)
    cv = SimpleView(c)

    msg = 'hello from b'
    b.notify_children(message=msg)
    assert av.value is None
    assert cv.value is None
    assert 'node_id' in bv.value
    assert bv.value['message'] == msg

    msg = 'hello from a'
    a.notify_children(message=msg)
    assert 'node_id' in av.value
    assert av.value['message'] == msg
    assert 'node_id' in bv.value
    assert bv.value['message'] == msg
    assert 'node_id' in cv.value
    assert cv.value['message'] == msg


class DataView(View):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = None

    def notify_view(self, message):
        node_id = message["node_id"]
        self.data = self.graph_nodes[node_id].request_data()


def test_two_children_request_data():
    a = Node(lambda: 5)
    b = node(lambda x: x - 2)(x=a)
    c = node(lambda x: x + 2)(x=a)
    av = DataView(a)
    bv = DataView(b)
    cv = DataView(c)

    msg = 'hello from a'
    a.notify_children(message=msg)
    assert av.data == 5
    assert bv.data == 3
    assert cv.data == 7


def test_data_request_is_cached():
    global log
    log = ''

    def log_and_call(n, f, x=None):
        global log
        log += n
        if x is None:
            return f()
        else:
            return f(x)

    a = Node(partial(log_and_call, n='a', f=lambda: 5))
    b = node(partial(log_and_call, n='b', f=lambda x: x - 2))(x=a)
    c = node(partial(log_and_call, n='c', f=lambda x: x + 2))(x=a)
    d = node(partial(log_and_call, n='d', f=lambda x: x**2))(x=c)
    av = DataView(a)  # noqa: F841
    bv = DataView(b)  # noqa: F841
    cv = DataView(c)  # noqa: F841
    dv = DataView(d)  # noqa: F841

    a.notify_children(message='hello from a')
    assert log == 'abcd'  # 'a' should only appear once in the log
    log = ''
    c.notify_children(message='hello from c')
    assert log == 'cd'  # 'c' requests data from 'a' but 'a' is cached so no 'a' in log


def test_remove_node():
    a = Node(lambda: 5)
    b = node(lambda x: x - 2)(x=a)
    c = node(lambda x: x + 2)(x=a)
    bv = DataView(b)
    cv = DataView(c)
    assert 'x' in b.kwparents
    assert a is b.kwparents['x']
    assert b in a.children
    assert c in a.children
    assert bv in b.views
    b.remove()
    assert bv not in b.views
    assert b not in a.children
    assert c in a.children
    assert cv in c.views


def test_cannot_remove_node_with_children():
    a = Node(lambda: 5)
    b = node(lambda x: x - 2)(x=a)
    av = DataView(a)
    with pytest.raises(RuntimeError) as e:
        a.remove()
    assert "Cannot delete node" in str(e.value)
    assert b in a.children
    assert av in a.views
