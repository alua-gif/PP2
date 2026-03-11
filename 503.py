import re
S = input()
P = input()
matches = re.findall(re.escape(P), S)
print(len(matches))