import numpy as np

arr = np.array([[4, 1, 3, 2],
                [2, 1, 4, 3],
                [4, 3, 2, 1],
                [3, 2, 1, 4]])
bool = np.isin(arr, [2, 1, 10, 10])
print((arr == [4, 1, 3, 2]).all(axis=1).any())