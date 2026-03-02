def fibonacci(n):
    a, b = 0, 1
    count = 0
    while count < n:
        yield a
        a, b = b, a + b
        count += 1
n = int(input())
print(",".join(str(x) for x in fibonacci(n)))