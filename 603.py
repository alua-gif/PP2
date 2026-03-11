n = int(input())
words = input().split()
indexed_words = []
for index, word in enumerate(words):
    indexed_words.append(f"{index}:{word}")
print(" ".join(indexed_words))