n=int(input())
num=list(map(int,input().split()))
mx=max(num)
print((num.index(mx)+1))