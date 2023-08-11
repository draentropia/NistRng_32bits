import numpy as np


array = []

with open('/home/eortega/coding/cesga-qrng/output.txt', 'r') as file:
    for line in file.readlines():
        val = int(line.split("\n")[0])
        array.append(val)

narray = np.array(array)

print(narray)
