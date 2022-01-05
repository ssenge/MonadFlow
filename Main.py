from src.Flow import *

class A():
    def __rshift__(self, obj):
        return A()

a = lambda x: x+1
b = a

a0 = A()
aa = a0 >> a >> a >> a
print(aa)
