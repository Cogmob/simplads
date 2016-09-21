from compare import expect
from nose.plugins.attrib import attr
from simplads.simplad_monad.delta_type import DeltaType
from simplads.simplad_monad.namedtuples.bind_args import BindArgs
from simplads.simplad_monad.namedtuples.bound import Bound
from simplads.simplad_monad.namedtuples.wrapped_delta import WrappedDelta
import unittest

from simplads import ListSimplad

unit = ListSimplad.unit
bind = ListSimplad.bind
run = ListSimplad.run
apply_delta = ListSimplad.apply_delta

def get_echo(i):
    return echo

def echo(i):
    return i

def return_with_delta(delta):
    return lambda i: (i[0], [
        WrappedDelta(type=DeltaType.configured, delta=delta)])

class TestListSimplad(unittest.TestCase):
    def test_unit(self):
        expect(unit(echo)([1,2,3,4])).to_equal(([1,2,3,4], None))

    def test_bind_single_layer(self):
        def double(i):
            return BindArgs(bound=2*i[0], deltas=[
                WrappedDelta(type=DeltaType.default,
                delta=None)])

        bound_before = Bound(unbound=[1,2,3,4], annotation=None)
        after = bind(double)(
                BindArgs(bound=bound_before,
                deltas=[]))
        expect(after).to_equal((([2,4,6,8], None), []))

    def test_bind_with_deltas(self):
        def double(i):
            return BindArgs(bound=2*i[0], deltas=[
                WrappedDelta(type=DeltaType.list,
                delta=[
                    WrappedDelta(type=DeltaType.configured, delta='a'),
                    WrappedDelta(type=DeltaType.configured, delta='b')]),
                WrappedDelta(type=DeltaType.default, delta=None)])

        bound_before = Bound(unbound=[1,2,3,4], annotation=None)
        after = bind(double)(
                BindArgs(bound=bound_before,
                deltas=[]))
        expect(after).to_equal(
            BindArgs(
                bound=Bound(unbound=[2,4,6,8], annotation=None),
                deltas=[
                    WrappedDelta(type=DeltaType.list, delta=[
                        WrappedDelta(type=DeltaType.list, delta=[
                            WrappedDelta(
                                type=DeltaType.configured,
                                delta='a'),
                            WrappedDelta(
                                type=DeltaType.configured,
                                delta='b')]),
                        WrappedDelta(type=DeltaType.list, delta=[
                            WrappedDelta(
                                type=DeltaType.configured,
                                delta='a'),
                            WrappedDelta(
                                type=DeltaType.configured,
                                delta='b')]),
                        WrappedDelta(type=DeltaType.list, delta=[
                            WrappedDelta(type=DeltaType.configured,
                                delta='a'),
                            WrappedDelta(type=DeltaType.configured,
                                delta='b')]),
                        WrappedDelta(type=DeltaType.list, delta=[
                            WrappedDelta(type=DeltaType.configured,
                                delta='a'),
                            WrappedDelta(type=DeltaType.configured,
                                delta='b')])
                        ])]))
