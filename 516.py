import re 
s = input()
p = r"Name: (.+), Age: (\d+)"
res = re.search(p, s)
print(res.group(1), res.group(2))