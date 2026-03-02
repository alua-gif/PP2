def func(n, m):
    for i in range(n, m+ 1):
            yield i*i

n, m = map(int, input().split())

for i in func(n, m ):
    print(i)