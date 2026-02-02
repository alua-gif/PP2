n=int(input())
sur=input().split()
newbie=set()
for i in sur:
    if i in newbie:
        print("NO")
    else:
        print("YES")
        newbie.add(i)