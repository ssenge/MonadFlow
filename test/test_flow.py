import unittest

from src.Base import Functor, ApplicativeFunctor, Monad
from src.Flow import Top, Up, Flow, Down, Bottom, loop, lift_in, until, repeat, dowhile, succeed, fail, lift_out, lift, \
    loopV

inc = lift_in(lambda v: Up(v+1))
double = lift_in(lambda v: Up(2*v))
inc_f = lambda v: v+1

inc_up = lift_in(lambda v: Up(v+1))
inc_down = lift_in(lambda v: Down(v+1))


class TestFlow(unittest.TestCase):

    def test_instances(self):
        top = Top(0)
        self.assertIsInstance(top, Top)
        self.assertIsInstance(top, Flow)
        self.assertIsInstance(top, Monad)
        self.assertIsInstance(top, ApplicativeFunctor)
        self.assertIsInstance(top, Functor)
        self.assertIsInstance(top.v, int)

    def test_bind(self):
        #inc = lambda v: Up(v+1)

        # Up
        up0 = Up(0)
        up1 = up0.bindM(inc)
        self.assertEqual(up1.v, 1)

        up2 = up1.bindM(inc).bindM(inc)
        self.assertEqual(up2.v, 3)

        # Down
        down0 = Down(0)
        down1 = down0.bindM(inc)
        self.assertEqual(down1.v, 0)

        down2 = down1.bindM(inc).bindM(inc)
        self.assertEqual(down2.v, 0)

        # Top
        top0 = Top(0)
        top1 = top0.bindM(inc)
        self.assertEqual(top1.v, 0)

        top2 = top1.bindM(inc).bindM(inc)
        self.assertEqual(top2.v, 0)

        # Bottom
        bottom0 = Bottom(0)
        bottom1 = bottom0.bindM(inc)
        self.assertEqual(bottom1.v, 0)

        bottom2 = bottom1.bindM(inc).bindM(inc)
        self.assertEqual(bottom2.v, 0)

    def test_bind_op(self):
        #inc = lambda v: Up(v+1)

        # Up
        up0 = Up(0)
        up1 = up0 >> inc
        self.assertEqual(up1.v, 1)

        up2 = up1 >> inc >> inc
        self.assertEqual(up2.v, 3)

        down0 = Down(0)
        down1 = down0 << inc_down << inc_down
        self.assertEqual(down1.v, 2)


    def test_then(self):
        #inc_up = lambda v: Up(v+1)
        #inc_down = lambda v: Down(v+1)
        down0 = Down(0)
        down1 = down0.thenM(inc_down).thenM(inc_down)
        self.assertEqual(down1.v, 2)

        down2 = down0.thenM(inc_up).thenM(inc_up)
        self.assertEqual(down2.v, 2)
        self.assertIsInstance(down2, Down)

        down3 = down0.thenM(inc_up).thenM(inc_up).flip().bindM(inc_up)
        self.assertEqual(down3.v, 3)
        self.assertIsInstance(down3, Up)
        ## Down(0) & inc_up & inc_up & flip | inc_up ## then flip needs to be a func as well (not only a methond)

    def test_then_op(self):
        #inc_down = lambda v: Down(v+1)
        down0 = Down(0)
        down1 = down0 << inc_down << inc_down
        self.assertEqual(down1.v, 2)

    def test_bind_then(self):
        #inc_up = lambda v: Up(v+1)
        #inc_down = lambda v: Down(v+1)
        down0 = Down(0)
        down1 = down0.bindM(inc_down).thenM(inc_down).thenM(inc_up).bindM(inc_down).bindM(inc_up)
        self.assertEqual(down1.v, 2)


    def test_bind_then_op(self):
        #inc_up = lambda v: Up(v+1)
        #inc_down = lambda v: Down(v+1)
        down0 = Down(0)
        down1 = down0 >> inc_down << inc_down << inc_up >> inc_down >> inc_up
        self.assertEqual(down1.v, 2)

    def test_fmap(self):
        #inc = lambda v: v+1
        up0 = Up(0)
        up1 = up0.fmap(inc_f)
        self.assertEqual(up1.v, 1)

        up2 = up1.fmap(inc_f).fmap(inc_f)
        self.assertEqual(up2.v, 3)

        # This is a type error (wrong input type) but it works in this special in the sense that no exception is thrown.
        # The return type, however, is not monadic.
        #up3 = up2.bind(inc_f) ## wrong but works in Python

        # At least wrong return type can be detected
        #self.assertNotIsInstance(up3, Flow)

        # This then throws an exception but an AttributeError as the return type of the first bind
        # is not monadic and hence has no bind() method.
        with self.assertRaises(TypeError):
            up2.bindM(inc_f)#.bind(inc_f)


    def test_is_same(self):
        up0 = Up(0)
        self.assertTrue(Up.is_same(up0))

        down0 = Down(0)
        self.assertFalse(Up.is_same(down0))


    def test_get(self):
        down0 = Down(0)
        up0 = Up.get(down0)
        self.assertIsInstance(up0, Up)
        self.assertEqual(up0.v, 0)

        top0 = Top.get(up0)
        self.assertIsInstance(top0, Top)
        self.assertEqual(top0.v, 0)


    def test_norm(self):
        self.assertIsInstance(Top(0).norm(), Up)
        self.assertIsInstance(Up(0).norm(), Up)
        self.assertIsInstance(Down(0).norm(), Down)
        self.assertIsInstance(Bottom(0).norm(), Down)


    def test_flip(self):
        self.assertIsInstance(Top(0).flip(), Bottom)
        self.assertIsInstance(Up(0).flip(), Down)
        self.assertIsInstance(Down(0).flip(), Up)
        self.assertIsInstance(Bottom(0).flip(), Top)


    def test_norm_flip(self):
        self.assertIsInstance(Top(0).norm_flip(), Down)
        self.assertIsInstance(Up(0).norm_flip(), Down)
        self.assertIsInstance(Down(0).norm_flip(), Up)
        self.assertIsInstance(Bottom(0).norm_flip(), Up)




    def test_loop(self):
        n = 5000
        up0 = Up(0).bindM(loop(inc, lambda fm, _: fm.v != n))
        self.assertEqual(up0.v, n)


    def test_loop_escape(self):
        n = 2
        inc_up_top = lambda fm: Top(fm.v+1) if fm.v == n else Up(fm.v+1)
        up0 = Up(0) >> loop(inc_up_top, lambda *xs: True)
        self.assertEqual(up0.v, n+1)

        down0 = Down(0) << loop(inc_up_top, lambda *xs: True)
        self.assertEqual(down0.v, n+1)

    def test_until(self):
        n = 10
        up0 = Up(0) >> until(inc, lambda fm, _: fm.v == n)
        self.assertEqual(up0.v, n)


    def test_repeat(self):
        n = 10
        down0 = Down(0) << repeat(inc, n)
        self.assertEqual(down0.v, n)

    def test_dowhile(self):
        up0 = Up(0) >> dowhile(inc, lambda fm, n: n == 0)
        self.assertEqual(up0.v, 1)

    def test_succeed(self):
        up0 = Up(0) >> succeed(inc)
        self.assertEqual(up0.v, 1)

        inc_down_up = lambda fm: Up(fm.v+1) if fm.v == 2 else Down(fm.v+1)
        up0 = Up(0) >> succeed(inc_down_up)
        self.assertEqual(up0.v, 3)

    def test_fail(self):
        down0 = Down(0) << fail(inc_down)
        self.assertEqual(down0.v, 1)

        inc_up_down = lambda fm: Down(fm.v+1) if fm.v == 2 else Up(fm.v+1)
        up0 = Up(0) >> fail(inc_up_down)
        self.assertEqual(up0.v, 3)


    def test_to_flow(self):
        div = lambda x: 1/x

        up0 = Up(1)
        r0 = lift_in(div)(up0)
        self.assertEqual(r0, 1)

        up1 = Up(0)
        #r1 = lift_in(div)(up1) # As expected: ZeroDivisionError: division by zero
        #self.assertIsInstance(r1, Down)

        r2 = lift_out(div)(up1.v)
        self.assertIsInstance(r2, Down)

        r3 = lift(div)(up0)
        self.assertEqual(r3.v, 1)
        self.assertIsInstance(r3, Up)

        r4 = lift(div)(up1)
        self.assertIsInstance(r4, Down)


    def test_on(self):
        up0 = Up(0)
        up1 = up0 >> Up.on(inc)
        self.assertEqual(up1.v, 1)

        up2 = up1 >> Down.on(inc)
        self.assertEqual(up2.v, 1)


    def test_wfs(self):
        wf_bind = lambda fm: fm >> inc >> double
        wf_then = lambda fm: fm << inc << double
        up0 = Up(0)

        up1 = up0 >> wf_bind
        self.assertEqual(up1.v, 2)
        up2 = up1 >> wf_then
        self.assertEqual(up2.v, 6)

        down0 = Down(0)
        down1 = down0 >> wf_bind
        self.assertEqual(down1.v, 0)

        down2 = down1 << wf_then
        self.assertEqual(down2.v, 2)

        up3 = up2 >> repeat(wf_bind, 3)
        self.assertEqual(up3.v, 62)

    def test_bind(self):
        inc = lambda v: Up(v+1)
        inc_v = lambda v: v+1
        up0 = Up(0)
        up1 = up0.bind(inc)
        self.assertEqual(up1.v, 1)

        up2 = Up(up1.bind(loop(inc_v, lambda x, n: n < 2)))
        self.assertEqual(up2.v, 3)

        up3 = Up(up2 | loop(inc, lambda x, n: n < 5, extract=lambda fm: fm.extract()))
        self.assertEqual(up3.v, 8)

        up4 = Up(up3 | loopV(inc, lambda x, n: n < 5))
        self.assertEqual(up4.v, 13)


if __name__ == '__main__':
    unittest.main()
