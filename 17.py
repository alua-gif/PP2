import math
R = float(input())
x1, y1 = map(float, input().split())
x2, y2 = map(float, input().split())
dx = x2 - x1
dy = y2 - y1

a = dx*dx + dy*dy
b = 2*(x1*dx + y1*dy)
c = x1*x1 + y1*y1 - R*R
disc = b*b - 4*a*c

if disc < 0:
    if x1*x1 + y1*y1 <= R*R:
        length = math.sqrt(a)
    else:
        length = 0.0
else:
    t1 = (-b - math.sqrt(disc)) / (2*a)
    t2 = (-b + math.sqrt(disc)) / (2*a)
    t1, t2 = max(0, min(1, t1)), max(0, min(1, t2))
    length = max(0, abs(t2 - t1) * math.sqrt(a))

print("{:.10f}".format(length))