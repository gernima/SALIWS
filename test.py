a = 1
b = 2
c = [a, b]
tf = False
for x in [1, 2, 3]:
    for z in c:
        if z == x:
            tf = True
print(tf)
