import re
S = input()
D = input()
parts = re.split(D, S)
print(",".join(parts))