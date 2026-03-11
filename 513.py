import re
s = input()
p = r"\w+"
res = re.findall(p, s)
print(len(res)) 