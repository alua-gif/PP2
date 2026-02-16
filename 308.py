class Account:
    def __init__(self, owner, balance):
        self.owner = owner
        self.balance = balance

    def withdraw(self, amount):
        if amount <= self.balance:
            self.balance -= amount
            print(self.balance)
        else:
            print("Insufficient Funds")

B, W = map(int, input().split())
acc = Account("User", B)
acc.withdraw(W)

