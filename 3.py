a = {'a': {'z': 0, 't': 60}}
print([(v, k) for v, k in a.items()])
b = {v: a[v] for v, k in a.items()}
for k in a.keys():
    a[k].update({'t': 0})
print(b)
