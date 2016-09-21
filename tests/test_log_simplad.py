from compare import expect
from nose.plugins.attrib import attr
from simplads.simplad_monad.namedtuples.bind_args import BindArgs
from simplads.simplad_monad.namedtuples.bound import Bound
from simplads.simplad_monad.namedtuples.wrapped_delta import WrappedDelta
from simplads.simplad_monad.simplad_monad import DeltaType
import unittest

from simplads import LogSimplad, LogDeltaMaker

unit = LogSimplad.unit
bind = LogSimplad.bind
run = LogSimplad.run
apply_delta = LogSimplad.apply_delta

def get_echo(i):
    return lambda j: i

def echo(i):
    return i

def return_with_delta(delta):
    return lambda i: BindArgs(bound=i[0], deltas=[delta])

def return_with_wrapped_delta(delta):
    return lambda i: return_with_delta(
        WrappedDelta(type=DeltaType.configured,
        delta=delta))(i)

class TestLogSimplad(unittest.TestCase):
    def get_listener_func(self):
        return lambda i: self.log.append(i)

    def test_unit(self):
        expect(unit(echo)(4)).to_equal((4, {}))

    def test_bind_single_layer(self):
        bound_before = Bound(unbound=4, annotation={})
        delta = (['one'], [])
        result = BindArgs(bound=8, deltas=['delts', WrappedDelta(type=DeltaType.configured,
            delta=delta)])

        after = bind(get_echo(result))(
            BindArgs(bound=bound_before, deltas=['delts']))
        expect(after).to_equal(((8, {}), ['delts']))

    def test_bind_two_layers(self):
        bound_before = Bound(
                unbound=Bound(unbound=4, annotation={}), annotation={})
        delta = WrappedDelta(type=DeltaType.configured, delta=([], []))
        result = BindArgs(bound=8, deltas=['delts', delta, delta])

        after = bind(bind(get_echo(result)))(
            BindArgs(bound=bound_before, deltas=['delts']))
        expect(after).to_equal((((8, {}), {}), ['delts']))

    def test_single_message(self):
        def add_to_log(log, message):
            log.append(message)
            return log
        bound_before = Bound(unbound=4, annotation={'log': (add_to_log, [])})
        delta = (['one'], [])
        result = BindArgs(bound=8, deltas=['delts',
            WrappedDelta(type=DeltaType.configured, delta=delta)])

        res = bind(get_echo(result))(
                BindArgs(bound=bound_before, deltas=['delts']))
        (value, listeners), deltas = res
        func, log = listeners['log']
        expect(log).to_equal(['one'])

    def test_make_with_listener(self):
        bound_before = unit(echo)(4)
        delta = LogDeltaMaker.messages_and_listener([])

        args = bind(return_with_wrapped_delta(delta))(
            BindArgs(bound=bound_before, deltas=['delts']))

        result = BindArgs(bound=8, deltas=['delts',
            WrappedDelta(type=DeltaType.configured, delta=(['one'], []))])

        res = bind(get_echo(result))(BindArgs(bound=args.bound, deltas=[]))

        (value, listeners), deltas = res
        func, log = listeners['log']
        expect(log).to_equal(['one'])

    def test_merge_deltas(self):
        bound_before = unit(echo)(4)

        delta = WrappedDelta(type=DeltaType.list, delta=[
            WrappedDelta(
                delta=LogDeltaMaker.messages_and_listener(['one']),
                type=DeltaType.configured),
            WrappedDelta(
                delta=LogDeltaMaker.messages(['two']),
                type=DeltaType.configured)
        ])

        args = bind(return_with_delta(delta))(
            BindArgs(bound=bound_before, deltas=['higher delts']))

        result = BindArgs(bound=8, deltas=['delts',
            WrappedDelta(type=DeltaType.configured, delta=(['three'], []))])

        res = bind(get_echo(result))(BindArgs(bound=args.bound, deltas=[]))
        (value, listeners), deltas = res
        func, log = listeners['log']
        expect(log).to_equal(['one', 'two', 'three'])
