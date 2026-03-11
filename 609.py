n = int(input())
keys = input().split()
values = input().split()

data_dict = dict(zip(keys, values))
query = input().strip()
print(data_dict.get(query, "Not found"))