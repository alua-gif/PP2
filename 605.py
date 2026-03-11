S = input().strip().lower()
vowels = "aeiou"
if any(c in vowels for c in S):
    print("Yes")
else:
    print("No")