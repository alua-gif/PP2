import json
def deep_diff(a, b, path=""):
    diffs = []
    keys = set(a.keys()) | set(b.keys())

    for key in sorted(keys):
        new_path = f"{path}.{key}" if path else key

        if key not in a:
            diffs.append((new_path, "<missing>", json.dumps(b[key], separators=(",", ":"))))
        elif key not in b:
            diffs.append((new_path, json.dumps(a[key], separators=(",", ":")), "<missing>"))
        elif isinstance(a[key], dict) and isinstance(b[key], dict):
            diffs.extend(deep_diff(a[key], b[key], new_path))
        elif a[key] != b[key]:
            diffs.append((
                new_path,
                json.dumps(a[key], separators=(",", ":")),
                json.dumps(b[key], separators=(",", ":"))
            ))
    return diffs
A = json.loads(input())
B = json.loads(input())

differences = deep_diff(A, B)

if not differences:
    print("No differences")
else:
    for path, old, new in sorted(differences):
        print(f"{path} : {old} -> {new}")