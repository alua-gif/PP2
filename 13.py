import json
import re
def resolve_query(data, query):
    tokens = re.findall(r'[a-zA-Z_]\w*|\[\d+\]', query)

    for token in tokens:
        if token.startswith('['):
            index = int(token[1:-1])
            if isinstance(data, list) and 0 <= index < len(data):
                data = data[index]
            else:
                return "NOT_FOUND"
        else:
            if isinstance(data, dict) and token in data:
                data = data[token]
            else:
                return "NOT_FOUND"
    return json.dumps(data, separators=(",", ":"))

J = json.loads(input())
q = int(input())

for _ in range(q):
    query = input()
    result = resolve_query(J, query)
    print(result)