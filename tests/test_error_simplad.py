from compare import expect
from nose.plugins.attrib import attr
from simplads.simplad_monad.namedtuples.bind_args import BindArgs
from simplads.simplad_monad.namedtuples.delta_overwrite import DeltaOverwrite
from simplads.simplad_monad.simplad_base_helper import WrappedDelta, Bound
from simplads.simplad_monad.simplad_monad import DeltaType
import unittest

from simplads import ErrorSimplad, ErrorDeltaMaker, ErrorType, ErrorRes

unit = ErrorSimplad.unit
bind = ErrorSimplad.bind
run = ErrorSimplad.run
apply_delta = ErrorSimplad.apply_delta

def echo(i):
    return i

def get_echo(i):
    return lambda j: i

class TestErrorSimplad(unittest.TestCase):
    def test_unit(self):
        res = unit(echo)(4)
        expect(res).to_equal((4,ErrorType.none))

    def test_run_when_is_value(self):
        expect(run(get_echo(4), ErrorType.none, 2, 'higher deltas')).to_equal(4)

    def test_run_when_no_value(self):
        expect(run(get_echo(4),
            ErrorType.error,
            2,
            ['higher deltas', True])).to_equal(
                BindArgs(bound=2, deltas=['higher deltas', True]))

    def test_apply_delta_has_value_to_has_value(self):
        expect(apply_delta(ErrorType.none, ErrorDeltaMaker.no_error(), 5)).to_equal(
                (ErrorType.none, DeltaOverwrite()))

    def test_apply_delta_has_value_to_no_value(self):
        expect(apply_delta(ErrorType.error, ErrorDeltaMaker.no_error(), 4)).to_equal(
                (ErrorType.none, DeltaOverwrite()))

    def test_bind_has_value_to_has_value(self):
        result_value = BindArgs(bound=8, deltas=['higher deltas',
            WrappedDelta(type=DeltaType.default, delta=None)])
        higher_deltas = ['higher deltas']
        bound_before = Bound(unbound=4, annotation=ErrorType.none)

        bound_result, higher_deltas = bind(
                get_echo(result_value))(
                        BindArgs(bound=bound_before, deltas=higher_deltas))
        expect(bound_result).to_equal(
                Bound(unbound=8, annotation=ErrorType.none))
        expect(higher_deltas).to_equal(['higher deltas'])

    def test_bind_has_value_to_has_no_value(self):
        result_value = BindArgs(
            bound='value',
            deltas=['higher deltas',
            WrappedDelta(
                type = DeltaType.configured,
                delta=ErrorDeltaMaker.error('error text'))])
        higher_deltas = ['higher deltas']
        bound_before = Bound(unbound=4, annotation=ErrorType.none)

        bound_result, higher_deltas = bind(get_echo(result_value))(BindArgs(
            bound=bound_before, deltas=higher_deltas))
        expect(bound_result).to_equal(Bound(
            unbound=ErrorRes(
                has_error=True,
                result='value',
                error_text='error text'), annotation=ErrorType.error))
        expect(higher_deltas).to_equal(['higher deltas'])

    def test_bind_has_no_value_to_has_value(self):
        result_delta = WrappedDelta(type=DeltaType.configured,
                delta=ErrorDeltaMaker.error('error text'))
        higher_deltas_after = ['higher deltas', result_delta]
        result_value = BindArgs(bound=None, deltas=higher_deltas_after)
        higher_deltas_before = ['higher deltas']
        bound_before = Bound(unbound=4, annotation=ErrorType.none)

        bound_result, higher_deltas = bind( get_echo(result_value))(
            BindArgs(bound=bound_before, deltas=higher_deltas_before))

        expect(bound_result).to_equal(
            Bound(unbound=ErrorRes(has_error=True, error_text='error text'),
            annotation=ErrorType.error))
        expect(higher_deltas).to_equal(['higher deltas'])

    def test_bind_two_layers(self):
        bound_before = Bound(
                unbound=Bound(unbound=4, annotation=ErrorType.none),
                annotation=ErrorType.none)
        result = BindArgs(bound=8, deltas=[
            'higher deltas',
            WrappedDelta(type=DeltaType.default, delta=True),
            WrappedDelta(type=DeltaType.default, delta=True)])

        after = bind(bind(get_echo(result)))(
                BindArgs(bound=bound_before, deltas=['higher deltas']))
        outer_bound, deltas = after
        inner_bound, outer_annotation = outer_bound
        value, inner_annotation = inner_bound
        expect(outer_annotation).to_equal(ErrorType.none)
        expect(inner_annotation).to_equal(ErrorType.none)
        expect(value).to_equal(8)
        expect(deltas[0]).to_equal('higher deltas')

    def test_merge_deltas(self):
        result_value = BindArgs(bound=8, deltas=[
            'higher deltas', WrappedDelta(type=DeltaType.list, delta=[
                WrappedDelta(type=DeltaType.default, delta=None),
                WrappedDelta(
                    type=DeltaType.configured,
                    delta=ErrorDeltaMaker.finish())])])
        higher_deltas = ['higher deltas']
        bound_before = Bound(unbound=4, annotation=ErrorType.none)

        bound_result, higher_deltas = bind(get_echo(result_value))(
            BindArgs(bound=bound_before, deltas=higher_deltas))
        expect(bound_result).to_equal(Bound(
            unbound=ErrorRes(has_error=False, result=8),
            annotation=ErrorType.finish))
        expect(higher_deltas).to_equal(['higher deltas'])
