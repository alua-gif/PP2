n = int(input())
numbers = list(map(int, input().split()))
usnumbers = sorted(set(numbers))
print(*(usnumbers))