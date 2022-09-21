# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp import Node, node, View


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
        self.data = self._graph_nodes[node_id].request_data()


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
