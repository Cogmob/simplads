from compare import expect
from nose.plugins.attrib import attr
from simplads.simplad_monad.simplad_base_helper import Bound
import unittest

from simplads import Bundle
from simplads import MaybeSimplad, MaybeDeltaMaker
from simplads import WriterDeltaMaker
from simplads import ReaderDeltaMaker

from simplads import fin
from simplads import retu

lift = Bundle.lift
res = Bundle.res

class TestBundle(unittest.TestCase):
    def test_no_simplads(self):
        s = Bundle().unit(4)
        result = s.pipe([
            lift(lambda i: 2*i),
            lift(lambda i: 2*i),
            lift(lambda i: 2*i)
        ])
        expect(s.bound).to_equal(32)
        expect(result).to_equal(32)

    def test_unit_with_maybe_simplad(self):
        s = Bundle().set_simplads({
            'a': MaybeSimplad()
        }).unit(unbound=4)
        expect(s.bound).to_equal(Bound(unbound=4, annotation=True))

    def test_maybe_simplad(self):
        s = Bundle().set_simplads({
            'a': MaybeSimplad()
        }).unit(4)
        s.pipe([
            lift(lambda i: 2*i),
            lambda i: res(val=2*i),
            lift(lambda i: 2*i)
        ])
        expect(s.bound).to_equal(Bound(unbound=32, annotation=True))

    def test_maybe_simplad_no_value(self):
        s = Bundle().set_simplads({
                'a': MaybeSimplad()
            }).unit(4)
        result = s.pipe([
            lift(lambda i: 2*i),
            lambda i: res(val=2*i),
            lambda i: res(delta_map={
                'a': MaybeDeltaMaker.no_value
            }),
            lift(lambda i: 2*i)
        ])
        expect(s.bound).to_equal(Bound(unbound=None, annotation=False))
        expect(result).to_equal(Bound(unbound=None, annotation=False))

    def test_write_and_read_obj(self):
        obj={}

        write = Bundle.delta('writer',
            WriterDeltaMaker.data(keys=['key'], new_data='val'))
        read = Bundle.delta_map(delta_map={'reader':
            ReaderDeltaMaker.read(['key'])
        })
        result = 'not set'
        def set_read_val(i):
            result = i.read_val
            return i

        s = Bundle().add_writer(obj).add_reader(obj).unit().pipe([
            write,
            read,
            lift(set_read_val)
        ])

        expect(result).to_equal('not set')

    def test_fin(self):
        def double_s(i): return 2*i
        double = lift(double_s)
        res = fin(1).add_error().pipe(double, double, double)
        expect(res).to_equal(8)

    #@attr('s')
    def test_error_happens_end(self):
        def double(i): return retu.rn(2*i)
        def error(i): return retu.error(2*i, 'error text')
        res = fin(1).add_error().pipe(double, double, error)
        expect(res).to_equal(9)
        res = fin(1)
