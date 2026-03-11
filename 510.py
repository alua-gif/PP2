import re
text = input()
pattern = r"cat|dog"
if re.search(pattern, text):
    print("Yes")
else:
    print("No")