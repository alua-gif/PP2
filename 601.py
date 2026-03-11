n = int(input())
def square(x):
    return int(x) ** 2
result = sum(map(square, input().split()))
print(result)