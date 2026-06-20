import numpy as np

X = np.load("X.npy", allow_pickle=True)
y = np.load("y.npy", allow_pickle=True)

X_new = []
y_new = []

for x, label in zip(X, y):
    if label != "stop":
        X_new.append(x)
        y_new.append(label)

X_new = np.array(X_new)
y_new = np.array(y_new)

np.save("X.npy", X_new)
np.save("y.npy", y_new)