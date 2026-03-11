import re
s = input()
p = r"\d"
def repl(match):
        return match.group(0)*2
result = re.sub(p, repl, s)
print(result)