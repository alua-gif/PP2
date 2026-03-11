import re
S = input()
P = input()
if re.search(P, S):
    print("Yes")
else:
    print("No")