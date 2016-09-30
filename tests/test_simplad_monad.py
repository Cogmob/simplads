from simplads.simplad_monad.simplad_base_helper import Bound

from compare import expect
from fn import F
from functools import partial
from nose.plugins.attrib import attr
from simplads.simplad_monad.namedtuples.bind_args import BindArgs
from simplads.simplad_monad.simplad_base_helper import WrappedDelta, Bound
from simplads.simplad_monad.simplad_monad import (
        DeltaType,
        SimpladMonad as SM,
        SimpladResult)
from simplads.simplads.list_simplad import ListSimplad
from simplads.simplads.log_simplad import LogSimplad
from simplads.simplads.maybe_simplad import MaybeSimplad as MS, MaybeType
import unittest

def get_echo(i):
    def f(j):
        return i
    return f

def echo(i):
    return i

def add_delta_map(i):
    return SimpladResult(value=i, delta_map={})

def add_customs(i):
    return i, {}

class TestSimpladMonad(unittest.TestCase):
    def test_fm(self):
        func = SM.get_four()
        expect(func).to_equal(4)

    def test_unit_maybe(self):
        add_simplads = SM.add_simplads({
            's1': MS(),
            's2': MS(),
            's3': MS(),
           's4': MS() })
        order = SM.set_simplad_order(['s1','s2','s3','s4'])

        sm = (F() >> add_simplads >> order)(SM.make())

        res = SM.unit(sm)(4)
        expect(res).to_equal(((((4, MaybeType.has_value), MaybeType.has_value),
            MaybeType.has_value), MaybeType.has_value))

    def test_unit_list(self):
        add_simplads = SM.add_simplads({
            'm1': MS(),
            's1': ListSimplad(),
            's2': ListSimplad(),
           's3': ListSimplad(),
            's4': ListSimplad(), })
        order = SM.set_simplad_order(['s1','s2','s3','s4','m1'])

        sm = (F() >> add_simplads >> order)(SM.make())

        val = [[[[1,2]],[[1]]],[[[4]]]]
        res = SM.unit(sm)(val)
        expect(res).to_equal(
            ([([([([(1, MaybeType.has_value), (2, MaybeType.has_value)],
            None)], None), ([([(1, MaybeType.has_value)], None)], None)],
            None), ([([([(4, MaybeType.has_value)], None)], None)], None)],
            None))

    def test_box_four(a):
        add_simplads = SM.add_simplads({
            's1': ListSimplad(),
            's2': ListSimplad(),
            's3': ListSimplad(),
            's4': ListSimplad()})
        order = SM.set_simplad_order(['s4','s3','s2','s1'])

        sm = (F() >> add_simplads >> order)(SM.make())

        boxed = SM.get_box(sm)(lambda x: x)(
            BindArgs(bound=SimpladResult(val=8,
                    delta_map={'s2': MaybeType.no_value}), deltas=[]))

        expect(boxed).to_equal(
           BindArgs(bound=8, deltas=[
               WrappedDelta(type=DeltaType.default, delta=None),
               WrappedDelta(type=DeltaType.configured,
                   delta=MaybeType.no_value),
               WrappedDelta(type=DeltaType.default, delta=None),
               WrappedDelta(type=DeltaType.default, delta=None)]))

    def test_bind_maybe(self):
        add_simplads = SM.add_simplads({
            '1': MS(),
            '2': MS(),
            '3': MS(),
            '4': MS(),
            '5': MS()
            })
        order = SM.set_simplad_order(['1','2','3','4','5'])

        sm = (F() >> add_simplads >> order)(SM.make())

        val = 4
        bound = SM.unit(sm)(val)

        def double_simplad_result(i):
            return SimpladResult(val=i*2, delta_map={})

        bound = SM.bind(double_simplad_result)(
                (sm, BindArgs(bound=bound, deltas=[])))
        bound = SM.bind(double_simplad_result)(bound)
        bound = SM.bind(double_simplad_result)(bound)
        bound = SM.bind(double_simplad_result)(bound)
        bound = SM.bind(double_simplad_result)(bound)
        bound = SM.bind(double_simplad_result)(bound)
        bound = SM.bind(double_simplad_result)(bound)

        expect(bound[1].bound).to_equal(
            Bound(unbound=Bound(unbound=Bound(unbound=Bound(unbound=Bound(
                unbound=512,
                annotation=MaybeType.has_value),
                annotation=MaybeType.has_value),
                annotation=MaybeType.has_value),
                annotation=MaybeType.has_value),
                annotation=MaybeType.has_value))

    def test_bind_list(self):
        add_simplads = SM.add_simplads({
            '1': ListSimplad(),
            '2': ListSimplad(),
            '3': ListSimplad(),
            '4': ListSimplad(),
            '5': ListSimplad()})
        order = SM.set_simplad_order(['1','2','3','4','5'])

        sm = (F() >> add_simplads >> order)(SM.make())

        val = [[[[[4]]]]]
        bound = SM.unit(sm)(val)

        def double_simplad_result(i):
            return SimpladResult(val=i*2, delta_map={})

        bound = SM.bind(double_simplad_result)(
                (sm, BindArgs(bound=bound, deltas=[])))
        bound = SM.bind(double_simplad_result)(bound)
        bound = SM.bind(double_simplad_result)(bound)
        bound = SM.bind(double_simplad_result)(bound)
        bound = SM.bind(double_simplad_result)(bound)
        bound = SM.bind(double_simplad_result)(bound)
        bound = SM.bind(double_simplad_result)(bound)

        expect(bound[1].bound).to_equal(
            Bound(unbound=[Bound(unbound=[Bound(unbound=[Bound(unbound=[Bound(
                unbound=[512],
                annotation=None)],
                annotation=None)],
                annotation=None)],
                annotation=None)],
                annotation=None))

    def test_bind_mixed(self):
        add_simplads = SM.add_simplads({
            '1': MS(),
            '2': MS(),
            '3': ListSimplad(),
            '4': ListSimplad(),
            '5': MS()
            })
        order = SM.set_simplad_order(['1','2','3','4','5'])

        sm = (F() >> add_simplads >> order)(SM.make())

        val = [[4]]
        bound = SM.unit(sm)(val)

        def double_simplad_result(i):
            return SimpladResult(val=i*2, delta_map={})

        bound = SM.bind(double_simplad_result)(
                (sm, BindArgs(bound=bound, deltas=[])))
        bound = SM.bind(double_simplad_result)(bound)
        bound = SM.bind(double_simplad_result)(bound)
        bound = SM.bind(double_simplad_result)(bound)
        bound = SM.bind(double_simplad_result)(bound)
        bound = SM.bind(double_simplad_result)(bound)
        bound = SM.bind(double_simplad_result)(bound)

        expect(bound[1].bound).to_equal(
            Bound(unbound=Bound(unbound=Bound(unbound=[Bound(unbound=[Bound(
                unbound=512,
                annotation=MaybeType.has_value)],
                annotation=None)],
                annotation=None),
                annotation=MaybeType.has_value),
                annotation=MaybeType.has_value))

    def test_bind_with_fail(self):
        add_simplads = SM.add_simplads({
            '1': MS(),
            '2': MS(),
            '3': ListSimplad(),
            '4': ListSimplad(),
            '5': MS()
            })
        order = SM.set_simplad_order(['1','2','3','4','5'])

        sm = (F() >> add_simplads >> order)(SM.make())

        val = [[4]]
        bound = SM.unit(sm)(val)

        def double_simplad_result(i):
            return SimpladResult(val=i*2, delta_map={})

        def double_simplad_result_fail_2(i):
            return SimpladResult(val=i*2, delta_map={
                '5': MaybeType.no_value
            })

        bound = SM.bind(double_simplad_result)(
                (sm, BindArgs(bound=bound, deltas=[])))
        bound = SM.bind(double_simplad_result)(bound)
        bound = SM.bind(double_simplad_result)(bound)
        bound = SM.bind(double_simplad_result_fail_2)(bound)
        bound = SM.bind(double_simplad_result)(bound)
        bound = SM.bind(double_simplad_result)(bound)
        bound = SM.bind(double_simplad_result)(bound)

        expect(bound[1].bound).to_equal(Bound(unbound=None,
            annotation=MaybeType.no_value))

#    def test_bind_with_fail(self):
#        add_simplads = SM.add_simplads({
#            's1': MS(),
#            's2': MS(),
#            's3': MS(),
#            's4': MS(),
#            's5': MS(),
#            's6': MS(),
#            's7': MS()
#        })
#        order = SM.set_simplad_order(['s7','s6','s5','s4','s3','s2','s1'])
#
#        sm = (F() >> add_simplads >> order)(SM.make())
#
#        unit = SM.unit(sm)
#        bind = SM.bind(
#            func = get_echo(Bound(unbound=8,
#                annotation={'s2':MaybeType.no_value})))
#
#        result = (F() >> unit >> add_deltas >> bind >> bind >> bind)(4)
#        expect(result).to_equal(
#            BindArgs(Bound(
#                unbound=Bound(unbound=None, annotation=MaybeType.no_value),
#                annotation=MaybeType.has_value), deltas=[]))

    def test_pushing_simplad(self):
        add_maybe = SM.push_simplad(simplad=MS())
        add_log = SM.push_simplad(simplad=LogSimplad())
        sm1 = (F() >> add_maybe >> add_maybe >> add_log)(SM.make())

        add_simplads = SM.add_simplads({
            '1': MS(),
            '2': MS(),
            '3': LogSimplad(),
        })
        order = SM.set_simplad_order(['1','2','3'])
        sm2 = (F() >> add_simplads >> order)(SM.make())

        expect(SM.unit(sm1)(4)).to_equal(SM.unit(sm2)(4))

    @attr('s')
    def test_pushing_simplad_bind(self):
        add_maybe = SM.push_simplad(simplad=MS())
        add_log = SM.push_simplad(simplad=LogSimplad())
        sm1 = (F() >> add_maybe >> add_maybe >> add_log)(SM.make())

        def box(sm):
            def f(i):
                return (sm, BindArgs(bound=i, deltas=[]))
            return f

        add_simplads = SM.add_simplads({
            '1': MS(),
            '2': MS(),
            '3': LogSimplad(),
        })
        order = SM.set_simplad_order(['1','2','3'])
        sm2 = (F() >> add_simplads >> order)(SM.make())

        bind1 = SM.bind(func = add_customs)
        bind2 = SM.bind(func = add_customs)

        binds1 = (F() >> SM.unit(sm1) >> box(sm1) >> bind1 >> bind1)(4)
        binds2 = (F() >> SM.unit(sm2) >> box(sm2) >> add_simplads >> bind2 >> bind2)(4)

        expect(binds1).to_equal(binds2)
