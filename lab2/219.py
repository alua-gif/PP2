n=int(input())
counts={}
for i in range(n):
    name, episodes=input().split()
    episodes=int(episodes)
    if name in counts:
        counts[name]+=episodes
    else:
        counts[name]=episodes
for name in sorted(counts):
    print(name, counts[name])