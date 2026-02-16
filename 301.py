n=input()
isValid=True
for x in n:
    if int(x)%2!=0:
        isValid=False
        
if isValid:
    print("Valid")
else:
    print("Not valid")