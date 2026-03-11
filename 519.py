import re
s = input()
p = re.compile(r"\w+")
res = p.findall(s)
print(len(res))