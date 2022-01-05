from src.Flow import Up, lift_in, lift, Down

#inc = lift_in(lambda v: Up(v+1))
inc = lift(lambda i: i+1)

i = Down(0)
o = lambda i: i << inc << inc >> inc
print(o(i).extract())

# Input >> complete
# c >> c
# c >> s

from goldpot import *

gp = Goldpot("sk-rpuk7WvrZYCY7v7nm2hzh88TfFhrBymtFTF0lIJA")
l = ['abc', 'ghi', 'def']
ci = CompletionInput(start="start\n", end="This is the first end sentence. This is the second end sentence.",
                     max_chars=69, samples=l)

complete = lift(lambda ci: gp.complete(ci))
o = Up(ci) >> complete  # >> out2in >> complete
print(o.extract())