import re
s = input()
p = re.compile(r"^\d+$")
res = p.findall(s)
if res:
    print("Match")
else:
    print("No match")