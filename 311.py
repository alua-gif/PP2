class Pair:
    def __init__(self,a,b):
        self.a = a
        self.b = b
    def add(self,new_a,new_b):
        self.a +=new_a
        self.b += new_b
        return self.a, self.b
    
    
a,b,c,d = map(int,input().split())
pair_f = Pair(a,b)
sum_num = pair_f.add(c,d)
print(f"Result: {sum_num[0]} {sum_num[1]}")