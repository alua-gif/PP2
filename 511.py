import re
s = input()
p = r"([A-Z])"
res = re.findall(p, s)
print(len(res))