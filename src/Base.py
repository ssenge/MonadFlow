from __future__ import annotations
from abc import ABCMeta, abstractmethod
from typing import Callable, Any, TypeVar, Generic

A = TypeVar('A')
B = TypeVar('B')


class Functor(Generic[A, B], metaclass=ABCMeta):

    # Type: f a -> (a -> b) -> f b
    @abstractmethod
    def fmap(self, f: Callable[[A], B]) -> Functor[B]:
        raise NotImplementedError


class ApplicativeFunctor(Functor):

    # Type : f (a -> b) -> f a -> f b
    @abstractmethod
    def apply(self, f: ApplicativeFunctor[Callable[[A], B]]) -> ApplicativeFunctor[B]:
        raise NotImplementedError


class Monad(ApplicativeFunctor):

    # Type: m a -> (a -> m b) -> m b
    @abstractmethod
    def bind(self, f: Callable[[A], Monad[B]]) -> Monad[B]:
        raise NotImplementedError

    # Type: a -> m a
    @staticmethod
    @abstractmethod
    def pure(v: A) -> Monad[A]:
        raise NotImplementedError

