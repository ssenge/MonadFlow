# FlowMonad

This library offers Python tools for creating monadic workflows. As a motivating example, the idea is to turn convoluted sequences like this:

```python
if r1 := func1():
    if r2 := func2(r2):
        if r3 := func3(r3):
            # ...
```
into clean code like this:
```python
r = func1() >> func2() >> func3() # ...
```
And this is just a glimpse, much more complicated cases could be transformed into simple expressions.

### No fear of Monads
Monads are usually considered a difficult to understand abstract concept with though underlying foundations in Category Theory with primary usage in functional programming like Haskell. Although all of this is correct, for our purposes a Monad is just a simple wrapper class around a simple value and three methods that conform to some simple rules. Basically, a (very) simple Python representation could look like:
```python
@dataclass
class Monad:
    T value
    def fmap(self):
        pass
    def apply(self):
        pass
    def bind(self):
        pass
```
The method fmap() already exists in Python for Iterables and is known as X.map(). The next one, apply(), is not required in our case and hence, discussion can be skipped.

The central piece of a Monand, where all the magic happens, is the last one: the famous bind() method. We skip here the discussion of the related monadic laws and just restrict ourself...tbd ;-)
