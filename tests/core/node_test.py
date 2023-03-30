# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from functools import partial

import pytest
from views import DataView, SimpleView

from plopp import Node, node


def test_two_nodes_parent_child():
    a = Node(lambda: 5)
    b = Node(lambda x: x - 2, x=a)
    assert 'x' in b.kwparents
    assert a is b.kwparents['x']
    assert b in a.children
    assert b() == 3


def test_two_nodes_notify_children():
    a = Node(lambda: 5)
    b = Node(lambda x: x - 2, x=a)
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
    b = Node(lambda x: x - 2, x=a)
    c = Node(lambda x: x + 2, x=a)
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


def test_two_children_request_data():
    a = Node(lambda: 5)
    b = Node(lambda x: x - 2, x=a)
    c = Node(lambda x: x + 2, x=a)
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
    b = Node(partial(log_and_call, n='b', f=lambda x: x - 2), x=a)
    c = Node(partial(log_and_call, n='c', f=lambda x: x + 2), x=a)
    d = Node(partial(log_and_call, n='d', f=lambda x: x**2), x=c)
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
    b = Node(lambda x: x - 2, x=a)
    c = Node(lambda x: x + 2, x=a)
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
    b = Node(lambda x: x - 2, x=a)
    av = DataView(a)
    with pytest.raises(RuntimeError, match="Cannot delete node"):
        a.remove()
    assert b in a.children
    assert av in a.views


def add(x, y):
    return x + y


def test_node_converts_raw_data_to_Node():
    a = Node(5)
    b = Node(add, x=a, y=2)
    assert a() == 5
    assert b.kwparents['x'] is a
    assert 'y' in b.kwparents
    assert b.kwparents['y']() == 2
    assert b() == 7


def test_node_names_from_args():
    n = Node(add, 1, 3)
    assert n.name == 'add(arg_0, arg_1)'


def test_node_names_from_kwargs():
    n = Node(add, x=1, y=3)
    assert n.name == 'add(x, y)'


def test_node_names_from_args_and_kwargs():
    n = Node(add, 4, y=35)
    assert n.name == 'add(arg_0, y)'


def test_node_name_from_raw_input():
    assert Node(5).name == 'Input <int=5>'
    assert Node(1.2).name == 'Input <float=1.2>'
    assert Node('hello').name == "Input <str='hello'>"
    assert Node([1, 2, 3]).name == 'Input <list>'


def test_input_node_value():
    v = 57.2
    a = Node(v)
    b = Node(lambda: v)
    assert a.input_value == v
    assert b.input_value is None


def test_is_input_node():
    a = Node(5)
    b = Node(lambda x: x - 2, x=a)
    assert a.is_input_node
    assert not b.is_input_node


def test_node_operator_add():
    a = Node(5)
    b = Node(2)
    c = a + b
    assert c() == 7


def test_node_operator_radd():
    a = Node(5)
    b = a + 6
    assert b() == 11


def test_node_operator_sub():
    a = Node(5)
    b = Node(2)
    c = a - b
    assert c() == 3


def test_node_operator_rsub():
    a = Node(5)
    b = a - 3
    assert b() == 2


def test_node_operator_mul():
    a = Node(5)
    b = Node(2)
    c = a * b
    assert c() == 10


def test_node_operator_rmul():
    a = Node(5)
    b = a * 6
    assert b() == 30


def test_node_operator_truediv():
    a = Node(5)
    b = Node(2)
    c = a / b
    assert c() == 2.5


def test_node_operator_rtruediv():
    a = Node(5)
    b = a / 2
    assert b() == 2.5


def test_node_decorator_args():
    @node
    def sub(x, y):
        return x - y

    a = Node(5.5)
    b = Node(3.1)
    c = sub(a, b)
    assert c() == 2.4


def test_node_decorator_kwargs():
    @node
    def mult(x, y):
        return x * y

    a = Node(6.0)
    b = Node(4.0)
    c = mult(x=a, y=b)
    assert c() == 24.0
