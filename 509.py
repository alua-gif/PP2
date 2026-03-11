import re
text = input()
pattern = r"\b\w{3}\b"
matches = re.findall(pattern, text)
print(len(matches))