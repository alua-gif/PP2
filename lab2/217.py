n=int(input())
count = {}
for i in range(n):
    number = input().strip()
    if number in count:
        count[number]+=1
    else:
        count[number]=1
ans=0
for number in count:
    if count[number] == 3:
        ans += 1 
print(ans)