import re 
s = input()
p = r"\d{2}/\d{2}/\d{4}"
res = re.findall(p, s)
print(len(res))