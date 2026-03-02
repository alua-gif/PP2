x1, y1 = map(float, input().split())
x2, y2 = map(float, input().split())
x2r, y2r = x2, -y2
t = y1 / (y1 - y2r)
x = x1 + t * (x2r - x1)

print("{:.10f} {:.10f}".format(x, 0.0))