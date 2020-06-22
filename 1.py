class A:
    def __init__(self):
        self.hp = 10


def f(enemy, arena=False):
    if (type(enemy) == int and (arena and enemy < 0)) or (type(enemy) != int and (not arena and enemy.hp < 0)):
        print(1)
    else:
        print(2)


enemy1 = A()
enemy2 = 20
f(enemy1)
f(enemy2, True)
