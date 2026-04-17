import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report



# 1. Загрузка данных
X = np.load("X.npy", allow_pickle=True)
y = np.load("y.npy", allow_pickle=True)

print("X shape:", X.shape)
print("y shape:", y.shape)


# 2. Проверка данных
print("Примеры меток:", np.unique(y))

# 3. Делим на train/test
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y  # важно для баланса классов
)


# 4. Модель
model = RandomForestClassifier(
    n_estimators=150,
    random_state=42
)


# 5. Обучение
model.fit(X_train, y_train)


# =========================
# 6. Проверка качества
# =========================
y_pred = model.predict(X_test)

print("\nAccuracy:", accuracy_score(y_test, y_pred))
print("\nClassification report:\n")
print(classification_report(y_test, y_pred))


# =========================
# 7. Сохранение модели
# =========================
joblib.dump(model, "gesture_model.pkl")

print("\nМодель сохранена: gesture_model.pkl")
print(model.predict([X[0]]))
print(model.predict([X[10]]))
print(model.predict([X[50]]))

