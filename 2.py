def func(n):
    for i in range(0, n+ 1):
        if i % 2 == 0:
            yield i 
n = int(input())
first = True
for i in func(n):
    if not first:
        print(",", end="")
    print(i, end="")
    first = False