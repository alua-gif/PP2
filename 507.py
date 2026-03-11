import re
S = input()
P = input()
R = input()
result = re.sub(re.escape(P), R, S)
print(result)