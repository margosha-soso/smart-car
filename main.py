import numpy as np

y = np.load("y.npy", allow_pickle=True)

print(np.unique(y))