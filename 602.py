n = int(input())
def is_even(x):
    return int(x) % 2 == 0
evens = list(filter(is_even, input().split()))
print(len(evens))