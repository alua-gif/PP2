class Circle:
    pi = 3.14159
    def __init__(self,r):
        self.r = r
    def area(self):
        return (self.r**2)*Circle.pi

a = int(input())
cir = Circle(a)
areas = cir.area()
print(f"{areas:.2f}")