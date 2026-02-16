import math
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def show(self):
        print(f"({int(self.x)}, {int(self.y)})")
    def move(self, new_x, new_y):
        self.x = new_x
        self.y = new_y
    def dist(self, other): 
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

x1, y1 = map(int, input().split())
new_x, new_y = map(int, input().split())
x2, y2 = map(int, input().split())

p1 = Point(x1, y1)
p1.show()

p1.move(new_x, new_y)
p1.show()

p2 = Point(x2, y2)
print(f"{p1.dist(p2):.2f}")

