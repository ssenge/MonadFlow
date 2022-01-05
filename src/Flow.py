from __future__ import annotations

import traceback
from abc import abstractmethod, ABCMeta
from functools import partial
from typing import Callable, Any, TypeVar, Generic

from tco import *

from .Base import Monad

A = TypeVar('A')
B = TypeVar('B')


class Flow(Monad, Generic[A, B]):
    """ The Flow Monad base class. """

    def __init__(self, v: A):
        """ Constructor to put a value v in a Flow monad. """
        self.v = v

    def extract(self) -> A:
        """ Extracts the monadic value v. """
        return self.v

    @classmethod
    def pure(cls, v: A) -> Flow[A]:
        """ Wraps a value v in a Flow monad. """
        return cls(v)

    @classmethod
    def get(cls, fm: Flow[A]) -> Flow[A]:
        """ Creates a Flow monad m' a from m a (where m' is of the same type as self and m of fm). """
        return cls.pure(fm.v)

    @classmethod
    def is_same(cls, fm: Flow[A]) -> bool:
        """ Returns true if type(self) equals type(fm) """
        return cls is fm.__class__

    @classmethod
    def on(cls, wf: Callable[[Flow[A]], Flow[B]]) -> Flow[B]:
        """ Executes the workflow wf if fm is of the same type as cls. """
        return lambda fm: fm << wf if cls.is_same(fm) else fm

    def fmap(self, f: Callable[[A], B]) -> Flow[B]:
        """ Applies f to the monad's value and wraps the result also in a Flow monad. """
        return self.pure(f(self.v))

    def apply(self, f):
        raise NotImplementedError  # Currently not used and hence not implemented by subclasses

    @abstractmethod
    def bind(self, f: Callable[[A], Flow[B]]) -> Flow[B]:
        """ Standard monadic bind. """
        raise NotImplementedError

    # Type: m a -> (m a -> m b) -> m b
    @abstractmethod
    def bindM(self, f: Callable[[Flow[A]], Flow[B]]) -> Flow[B]:
        """ Similar to bind but f maps from m a (instead of a) to m b. """
        raise NotImplementedError

    @abstractmethod
    def then(self, f: Callable[[A], Flow[B]]) -> Flow[B]:
        """ Similar to bind but applies f in any case. """
        raise NotImplementedError

    @abstractmethod
    def thenM(self, f: Callable[[Flow[A]], Flow[B]]) -> Flow[B]:
        """ Similar to then but f maps from m a (instead of a) to m b. """
        raise NotImplementedError

    @abstractmethod
    def norm(self) -> Flow[A]:
        """ Turns an escalated instance (Top, Bottom) into a non-escalated one (Up, Down) (implementation in subclass). """
        raise NotImplementedError

    @abstractmethod
    def escalate(self) -> Flow[A]:
        """ Turns a non-escalated instance (Up, Down) into an escalated one (Top, Bottom) (implementation in subclass). """
        raise NotImplementedError

    @abstractmethod
    def flip(self) -> Flow[A]:
        """ Turns an instance in its opposite. """
        raise NotImplementedError

    def norm_flip(self) -> Flow[A]:
        """ Normalize then flip. """
        return self.norm().flip()

    def escalate_flip(self) -> Flow[A]:
        """ Escalate then flip. """
        return self.escalate().flip()

    # Assign operators to methods
    def __rshift__(self, f):
        return self.bindM(f)

    def __lshift__(self, f):
        return self.thenM(f)

    def __or__(self, f):
        return self.bind(f)

    def __and__(self, f):
        return self.then(f)


def to_flow(f=lambda x: x, x=None, down=None, up_func=lambda x, y: y):
    """ A general wrapping function to maps values that Python evaluates to True to an Up instance and to a Down else. """
    try:
        return Up(up_func(x, y)) if (y := f(x)) else Down(down if down else y)
    except Exception:
        return Down(traceback.format_exc())


# Some helper functions
ident = lambda x: x
lift_in = lambda f: lambda fm: f(fm.extract())
lift_out = lambda f: lambda fm: to_flow(f, fm)
lift_out_effect = lambda f: lambda fm: to_flow(f, fm, lambda x_, y_: x_)
lift_in_out = lambda f: lambda fm: lift_out(lift_in(f))(fm)
lift_in_out_effect = lambda f: lambda fm: lift_out_effect(lift_in(f))(fm)
lift = lift_in_out
lift_effect = lift_in_out_effect

# Control flow functions
loop = lambda f, cond, min_n=0, extract=ident: \
    C(lambda self: lambda x, n=0: self(extract(f(x)), n + 1)
    if (cond(x, n) or n < min_n) and not Top.is_same(x) and not Bottom.is_same(x) else x)()

dowhile = lambda f, cond, loop_f=loop: loop_f(f, cond, 1)
until = lambda f, cond, loop_f=loop: loop_f(f, lambda x, n: not cond(x, n))
repeat = lambda f, num, loop_f=loop: until(f, lambda _, n: n == num, loop_f)
succeed = lambda f: dowhile(f, lambda x, _: Bottom.is_same(x) or Down.is_same(x))
fail = lambda f: dowhile(f, lambda x, _: Top.is_same(x) or Up.is_same(x))

vloop = partial(loop, extract=lambda x: x.extract())
vdowhile = partial(dowhile, loop_f=vloop)
vuntil = partial(until, loop_f=vloop)
vrepeat = partial(repeat, loop_f=vloop)


class Escape(Flow, metaclass=ABCMeta):
    """ Base class for the two Flow instances (Top, Bottom) that could escape a control flow. """
    bind = lambda self, _: self  # just skip and do not apply a function
    bindM = bind
    then = bind
    thenM = then
    escalate = ident


class Top(Escape):
    """ Positive escape. """
    norm = lambda self: Up.get(self)
    flip = lambda self: Bottom.get(self)


class Bottom(Escape):
    """ Negative escape. """
    norm = lambda self: Down.get(self)
    flip = lambda self: Top.get(self)


class Up(Flow):
    """ Positive. """
    bind = lambda self, f: f(self.extract())
    bindM = lambda self, f: f(self)
    then = bind
    thenM = bindM
    norm = ident
    escalate = lambda self: Top.get(self)
    flip = lambda self: Down.get(self)


class Down(Flow):
    """ Negative. """
    bind = Escape.bind
    bindM = Escape.bindM
    then = lambda self, f: Down.get(f(self.extract()))
    thenM = lambda self, f: Down.get(f(self))
    norm = ident
    escalate = lambda self: Bottom.get(self)
    flip = lambda self: Up.get(self)
