import re
text = input()
pattern = r"^[a-zA-Z].*\d$"
if re.search(pattern, text):
    print("Yes")
else:
    print("No")