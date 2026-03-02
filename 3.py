def func(n):
    for i in range(0, n+ 1):
        if i % 12 == 0:
            yield i 
n = int(input())
for i in func(n + 1 ):
    print(i, end = " ")