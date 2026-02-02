x=int(input())
if x<=1:
    print("No")
else:
    prime = True
    for i in range(2,x):
        if x%i==0:
            prime=False 
            break
    if prime:
        print("Yes")
    else:
        print("No")