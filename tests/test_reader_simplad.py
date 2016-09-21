from compare import expect
from nose.plugins.attrib import attr
from simplads.simplad_monad.namedtuples.bind_args import BindArgs
from simplads.simplad_monad.namedtuples.delta_overwrite import DeltaOverwrite
from simplads.simplad_monad.simplad_base_helper import Bound
from simplads.simplad_monad.simplad_monad import DeltaType
from simplads.simplad_monad.simplad_monad import WrappedDelta
from simplads.simplads.reader_simplad import ReaderDeltaMaker, ReaderDelta, ReaderResult
import unittest

from simplads import ReaderSimplad as Monad

unit = Monad.unit
bind = Monad.bind
run = Monad.run
apply_delta = Monad.apply_delta

def get_echo():
    return echo

def echo(i):
    return i

def double(i):
    return BindArgs(bound=2*i.bound, deltas=i.deltas)

class TestReaderSimplad(unittest.TestCase):
    def test_unit(self):
        expect(unit(echo)([1,2,3,4]).unbound).to_equal([1,2,3,4])

    def test_bind_single_layer_no_read(self):
        bound_before = unit(echo)(4)
        after = bind(double)(BindArgs(bound=bound_before, deltas=[]))
        expect(after.bound.unbound).to_equal(8)

    def test_bind_single_layer_with_read(self):
        bound_before = unit(echo)(4)
        echo_this = BindArgs(bound=8,
                deltas=[WrappedDelta(type=DeltaType.configured,
                    delta=ReaderDeltaMaker.read(['key']))])
        after = bind(lambda i: echo_this)(BindArgs(bound=bound_before, deltas=[]))
        expect(after.bound.unbound).to_equal(
            ReaderResult(read_val='not initialised', val=8))

    def test_bind_two_layers(self):
        bound_before = Bound(
                unbound=Bound(unbound=1, annotation=8), annotation=9)
        after = bind(bind(double))(BindArgs(bound=bound_before, deltas=[]))
        expect(after).to_equal(BindArgs(bound=Bound(unbound=Bound(unbound=2,
            annotation=8), annotation=9), deltas=[]))

    def test_bind_twice(self):
        bound_before = Bound(unbound=1, annotation=[])

        after_first = bind(double)(BindArgs(bound=bound_before, deltas=[]))

        after_second = bind(double)(after_first)

        expect(after_second).to_equal(
                BindArgs(bound=Bound(unbound=4, annotation=[]), deltas=[]))

    def test_read(self):
        bound_before = Bound(unbound=1, annotation=[])

        obj = {'key': 'correct val'}

        echo_this = BindArgs(bound=8, deltas = [WrappedDelta(
            type=DeltaType.configured,
            delta=ReaderDeltaMaker.set_obj(keys=[], root_obj=obj))])

        after_first = bind(lambda i: echo_this)(BindArgs(
            bound=bound_before,
            deltas=[]))

        echo_this = BindArgs(bound=8, deltas = [WrappedDelta(
                type=DeltaType.configured,
                delta=ReaderDeltaMaker.read(['key']))])

        after_second = bind(lambda i: echo_this)(after_first)

        expect(after_second.bound.unbound).to_equal(
            ReaderResult(read_val='correct val', val=8))

    def test_read_deep(self):
        bound_before = Bound(unbound=1, annotation=[])

        obj = {'a': {'b': {'c': {'x': {'y': {'z': 'located'}}}}}}

        echo_this = BindArgs(bound=8, deltas = [WrappedDelta(
            type=DeltaType.configured,
            delta=ReaderDeltaMaker.set_obj(keys=[], root_obj=obj))])

        after_first = bind(lambda i: echo_this)(BindArgs(
            bound=bound_before,
            deltas=[]))

        echo_this = BindArgs(bound=8, deltas = [WrappedDelta(
                type=DeltaType.configured,
                delta=ReaderDeltaMaker.read(['a','b','c','x','y','z']))])

        after_second = bind(lambda i: echo_this)(after_first)

        expect(after_second.bound.unbound).to_equal(
            ReaderResult(read_val='located', val=8))

    def test_read_deep_overwrite(self):
        bound_before = Bound(unbound=1, annotation=[])

        obj = {'a': {'b': {'c': {'x': {'y': {'z': 'located'}}}}}}

        echo_this = BindArgs(bound=8, deltas = [WrappedDelta(
            type=DeltaType.configured,
            delta=ReaderDeltaMaker.set_obj(keys=[], root_obj=obj))])

        after_first = bind(lambda i: echo_this)(BindArgs(
            bound=bound_before,
            deltas=[]))

        echo_this = BindArgs(bound=8, deltas = [WrappedDelta(
                type=DeltaType.configured,
                delta=ReaderDeltaMaker.read(
                    ['a','b','c','x','y','z'],
                    overwrite=True))])

        after_second = bind(lambda i: echo_this)(after_first)

        expect(after_second.bound.unbound).to_equal('located')
