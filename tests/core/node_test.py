# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from functools import partial

import pytest

from plopp import Node, View, node


class DataView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = None

    def notify_view(self, message):
        node_id = message["node_id"]
        self.data = self.graph_nodes[node_id].request_data()


class SimpleView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = None

    def notify_view(self, message):
        self.value = message


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


def test_remove_node_args():
    a = Node(lambda: 5)
    b = Node(lambda x: x - 2, a)
    c = Node(lambda x: x + 2, a)
    bv = DataView(b)
    cv = DataView(c)
    assert a is b.parents[0]
    assert b in a.children
    assert c in a.children
    assert bv in b.views
    b.remove()
    assert bv not in b.views
    assert b not in a.children
    assert c in a.children
    assert cv in c.views


def test_remove_node_kwargs():
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


def test_remove_node_with_children_args():
    a = Node(lambda: 5)
    b = Node(lambda x: x - 2, a)
    av = DataView(a)
    a.remove()
    assert b not in a.children
    assert a not in b.parents
    assert a not in b.kwparents.values()
    assert av not in a.views


def test_remove_node_with_children_multiple_args():
    a = Node(lambda: 5)
    b = Node(lambda: 3)
    c = Node(lambda: 11)
    d = Node(lambda *args: sum(args), a, b, c)
    assert d() == 19
    a.remove()
    assert d() == 14
    b.remove()
    assert d() == 11
    c.remove()
    assert d() == 0


def test_remove_node_with_children_kwargs():
    a = Node(lambda: 5)
    b = Node(lambda x: x - 2, x=a)
    av = DataView(a)
    a.remove()
    assert b not in a.children
    assert a not in b.parents
    assert a not in b.kwparents.values()
    assert av not in a.views


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


def test_add_parent():
    a = Node(lambda: 5)
    b = Node(lambda x: x - 2)
    assert not a.children
    assert not b.parents
    assert not b.kwparents
    b.add_parents(a)
    assert a in b.parents
    assert b in a.children


def test_add_multiple_parents():
    a = Node(lambda: 5.0)
    b = Node(lambda: 12.0)
    c = Node(lambda: -3.0)
    d = Node(lambda x, y, z: x * y * z)
    d.add_parents(a, b, c)
    assert a in d.parents
    assert b in d.parents
    assert c in d.parents
    assert d in a.children
    assert d in b.children
    assert d in c.children


def test_add_kwparents():
    a = Node(lambda: 5)
    b = Node(lambda time: time * 101.0)
    assert not a.children
    assert not b.parents
    assert not b.kwparents
    b.add_kwparents(time=a)
    assert a is b.kwparents['time']
    assert b in a.children


def test_add_multiple_kwparents():
    a = Node(lambda: 5.0)
    b = Node(lambda: 12.0)
    c = Node(lambda: -3.0)
    d = Node(lambda x, y, z: x * y * z)
    d.add_kwparents(y=a, z=b, x=c)
    assert a is d.kwparents['y']
    assert b is d.kwparents['z']
    assert c is d.kwparents['x']
    assert d in a.children
    assert d in b.children
    assert d in c.children


def test_adding_same_child_twice_raises():
    a = Node(lambda: 5)
    with pytest.raises(ValueError, match="Node .* is already a child in"):
        Node(lambda x, y: x * y - 2, a, a)
    with pytest.raises(ValueError, match="Node .* is already a child in"):
        Node(lambda x, y: x * y - 2, x=a, y=a)


def test_adding_same_parent_twice_raises():
    a = Node(lambda: 5)
    b = Node(lambda x, y: x * y - 2)
    b.add_parents(a)
    with pytest.raises(ValueError, match="Node .* is already a parent in"):
        b.add_parents(a)


def test_adding_same_parent_twice_at_once_raises():
    a = Node(lambda: 5)
    b = Node(lambda x, y: x * y - 2)
    with pytest.raises(ValueError, match="Node .* is already a parent in"):
        b.add_parents(a, a)


def test_adding_same_kwparent_twice_raises():
    a = Node(lambda: 5)
    b = Node(lambda x, y: x * y - 2)
    with pytest.raises(ValueError, match="Node .* is already a child in"):
        b.add_kwparents(x=a, y=a)


def test_adding_same_view_twice_raises():
    a = Node(lambda: 15.0)
    av = SimpleView(a)
    with pytest.raises(ValueError, match="View .* is already a view in"):
        a.add_view(av)
