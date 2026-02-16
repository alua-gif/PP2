n=int(input())
for p in [2,3,5]:
    while n%p==0:
        n//=p 
if n==1:
    print("Yes")
else:
    print("No")