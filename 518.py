import re
s = input()
p = input()
patt = re.escape(p)
res = re.findall(patt, s)
print(len(res))