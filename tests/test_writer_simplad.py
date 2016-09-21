from compare import expect
from nose.plugins.attrib import attr
from simplads.simplad_monad.namedtuples.bind_args import BindArgs
from simplads.simplad_monad.simplad_base_helper import Bound
from simplads.simplad_monad.simplad_monad import DeltaType
from simplads.simplad_monad.simplad_monad import WrappedDelta
from simplads.simplads.writer_simplad import WriterDelta
import unittest

from simplads.simplads.writer_simplad import WriterSimplad, WriterDeltaMaker

unit = WriterSimplad.unit
bind = WriterSimplad.bind
run = WriterSimplad.run
apply_delta = WriterSimplad.apply_delta

def get_echo(i):
    return echo

def echo(i):
    return i

def double(i):
    return BindArgs(bound=2*i.bound, deltas=i.deltas)

class TestWriterSimplad(unittest.TestCase):
    def test_unit(self):
        expect(unit(echo)([1,2,3,4]).unbound).to_equal([1,2,3,4])

    def test_bind_single_layer(self):
        bound_before = Bound(unbound=1, annotation=[])
        after = bind(double)(BindArgs(bound=bound_before, deltas=[]))
        expect(after).to_equal(
                BindArgs(bound=Bound(unbound=2, annotation=[]), deltas=[]))

    def test_bind_two_layers(self):
        bound_before = Bound(
                unbound=Bound(unbound=1, annotation=[]), annotation=[])
        after = bind(bind(double))(BindArgs(bound=bound_before, deltas=[]))
        expect(after).to_equal(BindArgs(bound=Bound(unbound=Bound(unbound=2,
            annotation=[]), annotation=[]), deltas=[]))

    def test_bind_twice(self):
        bound_before = Bound(unbound=1, annotation=[])

        after_first = bind(double)(BindArgs(bound=bound_before, deltas=[]))

        after_second = bind(double)(after_first)

        expect(after_second).to_equal(
                BindArgs(bound=Bound(unbound=4, annotation=[]), deltas=[]))

    def test_write(self):
        bound_before = Bound(unbound=1, annotation=[])

        obj = {'key': 'not written'}

        result = BindArgs(bound=8, deltas = [WrappedDelta(
            type=DeltaType.configured,
            delta=WriterDeltaMaker.set_obj(
                new_data='a',
                keys=['key'],
                root_obj=obj))])

        after_first = bind(lambda i: result)(BindArgs(
            bound=bound_before,
            deltas=[WrappedDelta(
                type=DeltaType.configured,
                delta=None)]))

        after_second = bind(double)(after_first)

        expect(obj['key']).to_equal('a')

    def test_write_deep(self):
        bound_before = Bound(unbound=1, annotation=[])

        obj = {'a': {'b': {'c': {'x': {'y': {'z': 'not written'}}}}}}

        result = BindArgs(bound=8, deltas = [WrappedDelta(
            type=DeltaType.configured,
            delta=WriterDeltaMaker.set_obj(
                new_data='a',
                keys=['a','b','c','x','y','z'],
                root_obj=obj))])

        after_first = bind(lambda i: result)(BindArgs(
            bound=bound_before,
            deltas=[WrappedDelta(
                type=DeltaType.configured,
                delta=None)]))

        after_second = bind(double)(after_first)

        expect(obj['a']['b']['c']['x']['y']['z']).to_equal('a')
