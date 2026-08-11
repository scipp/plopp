# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026 Scipp contributors (https://github.com/scipp)

import asyncio

from plopp.widgets.debounce import debounce


def test_calls_immediately_without_running_event_loop():
    calls = []

    def callback(value):
        calls.append(value)

    debounced = debounce(callback, wait=0.01)
    debounced('first')
    debounced('second')

    assert calls == ['first', 'second']


def test_delays_call_and_keeps_latest_value_with_running_event_loop():
    async def run():
        calls = []
        called = asyncio.Event()

        def callback(value):
            calls.append(value)
            called.set()

        debounced = debounce(callback, wait=0.01)
        debounced('discarded')
        debounced('called')
        assert calls == []
        await asyncio.wait_for(called.wait(), timeout=1.0)
        return calls

    assert asyncio.run(run()) == ['called']


def test_independent_callbacks_do_not_cancel_each_other():
    async def run():
        calls = []
        both_called = asyncio.Event()

        def callback(value):
            calls.append(value)
            if len(calls) == 2:
                both_called.set()

        first = debounce(callback, wait=0.01)
        second = debounce(callback, wait=0.01)
        first('first')
        second('second')
        await asyncio.wait_for(both_called.wait(), timeout=1.0)
        return calls

    assert sorted(asyncio.run(run())) == ['first', 'second']
