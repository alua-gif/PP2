import re
s = input()
p = r"[0-9]{2,}"
res = re.findall(p, s)
print(" ".join(res)) #!!!!