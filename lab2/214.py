n=int(input())
a=list(map(int, input().split()))
cnt={}
for i in a:
    if i in cnt:
        cnt[i] += 1
    else:
        cnt[i] = 1

best_num = a[0]
best_count = cnt[best_num]

for i in cnt:
    if cnt[i] > best_count:
        best_count = cnt[i]
        best_num = i
    elif cnt[i] == best_count and i < best_num:
        best_num = i
print(best_num)