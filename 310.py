class Person:
    def __init__(self, name):
        self.name = name
class Student(Person):
    def __init__(self, name, gpa):
        super().__init__(name)
        self.gpa = gpa
    def display(self):
        print(f"Student: {self.name}, GPA: {self.gpa}")

a, b = map(str, input().split())
student = Student(a,float(b))
student.display() 