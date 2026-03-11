n = int(input())
A = list(map(int, input().split()))
B = list(map(int, input().split()))
total_sum = 0
for a, b in zip(A, B):
    total_sum += a * b
print(total_sum)