import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score
from collections import Counter

# =========================
# 1. ЗАГРУЗКА ДАННЫХ
# =========================

X = np.load("X.npy", allow_pickle=True)
y = np.load("y.npy", allow_pickle=True)

print("число классов:", Counter(y))
print(f"Loaded samples: {len(X)}")


# =========================
# 2. ПРОВЕРКА ДАННЫХ
# =========================

# проверяем, что все примеры одинаковой длины (64)
X_fixed = []
y_fixed = []

for xi, yi in zip(X, y):
    if len(xi) == 64:
        X_fixed.append(xi)
        y_fixed.append(yi)

X = np.array(X_fixed)
y = np.array(y_fixed)

print(f"After cleaning: {len(X)} samples")


# =========================
# 3. РАЗБИЕНИЕ DATASET
# =========================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# =========================
# 4. МОДЕЛЬ (ЛУЧШИЙ ВАРИАНТ)
# =========================

model = Pipeline([
    ("scaler", StandardScaler()),
    ("svc", SVC(
        kernel="rbf",
        C=10,
        gamma="scale",
        probability=True
    ))
])


# =========================
# 5. ОБУЧЕНИЕ
# =========================

model.fit(X_train, y_train)


# =========================
# 6. ПРОВЕРКА КАЧЕСТВА
# =========================

y_pred = model.predict(X_test)

print("\nAccuracy:", accuracy_score(y_test, y_pred))
print("\nClassification report:\n")
print(classification_report(y_test, y_pred))


# =========================
# 7. СОХРАНЕНИЕ МОДЕЛИ
# =========================

joblib.dump(model, "gesture_model.pkl")

print("\nModel saved as gesture_model.pkl")
