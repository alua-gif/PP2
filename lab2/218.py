n=int(input())
first={}
for i in range(n):
    s=input().strip()
    if s not in first:
        first[s]=i + 1
for s in sorted(first):
    print(s, first[s])