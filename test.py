from time import time

cur_time = time()
print(cur_time)
a = time()
n = 10
print(cur_time + n)
while int(a) != int(cur_time + n):
    a = time()
    # print(a, a == cur_time)
print(a)
print(a - cur_time)


