"""
@defgroup gesture_training Gesture Model Training
@brief Обучение модели машинного обучения для распознавания жестов рук.
@details
Этот модуль выполняет полный пайплайн обучения модели:
1. Загрузка и очистка датасета (X.npy, y.npy)
2. Разбиение на обучающую и тестовую выборки
3. Создание пайплайна: StandardScaler + SVM (RBF)
4. Обучение модели
5. Оценка качества (accuracy, classification report)
6. Сохранение обученной модели в файл gesture_model.pkl
"""

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

def load_dataset(X_path, y_path):
    """
    @brief Загружает датасет из файлов .npy.
    @param X_path   Путь к файлу с признаками (X.npy).
    @param y_path   Путь к файлу с метками (y.npy).
    @return         Кортеж (X, y) — массивы признаков и меток.
    """
    X = np.load(X_path, allow_pickle=True)
    y = np.load(y_path, allow_pickle=True)
    return X, y


def clean_dataset(X, y):
    """
    @brief Очищает датасет, удаляя примеры с некорректной длиной.
    @details
    Проверяет, что каждый вектор признаков имеет длину 64.
    @param X   Массив признаков.
    @param y   Массив меток.
    @return    Кортеж (X_clean, y_clean) — очищенные массивы.
    """
    X_clean = []
    y_clean = []

    for xi, yi in zip(X, y):
        if len(xi) == 64:
            X_clean.append(xi)
            y_clean.append(yi)

    return np.array(X_clean), np.array(y_clean)


def split_dataset(X, y, test_size=0.2, random_state=42):
    """
    @brief Разбивает датасет на обучающую и тестовую выборки.
    @param X            Массив признаков.
    @param y            Массив меток.
    @param test_size    Доля тестовой выборки (по умолчанию 0.2).
    @param random_state  Seed для воспроизводимости.
    @return             Кортеж (X_train, X_test, y_train, y_test).
    """
    return train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y
    )


def create_model():
    """
    @brief Создаёт пайплайн модели с предобработкой и SVM-классификатором.
    @details
    Пайплайн состоит из двух шагов:
    1. StandardScaler — нормализация признаков (среднее=0, дисперсия=1)
    2. SVC с ядром RBF (C=10, gamma='scale') — классификатор опорных векторов
    @return    Объект Pipeline (готовый к обучению).
    """
    return Pipeline([
        ("scaler", StandardScaler()),
        ("svc", SVC(
            kernel="rbf",
            C=10,
            gamma="scale",
            probability=True
        ))
    ])


def train_model(model, X_train, y_train):
    """
    @brief Обучает модель на тренировочных данных.
    @param model       Объект модели (Pipeline).
    @param X_train     Обучающие признаки.
    @param y_train     Обучающие метки.
    @return            Обученная модель.
    """
    model.fit(X_train, y_train)
    return model


def evaluate_model(model, X_test, y_test):
    """
    @brief Оценивает качество модели на тестовых данных.
    @param model     Обученная модель.
    @param X_test    Тестовые признаки.
    @param y_test    Тестовые метки.
    @return          Словарь с метриками: accuracy, report.
    """
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)
    
    return {
        "accuracy": accuracy,
        "report": report,
        "predictions": y_pred
    }


def save_model(model, filepath="gesture_model.pkl"):
    """
    @brief Сохраняет обученную модель в файл.
    @param model      Обученная модель.
    @param filepath   Путь для сохранения (по умолчанию "gesture_model.pkl").
    """
    joblib.dump(model, filepath)
    print(f"\nModel saved as {filepath}")


# =========================
# ОСНОВНАЯ ФУНКЦИЯ
# =========================

def main():
    """
    @brief Основная функция обучения модели.
    @details
    Последовательность шагов:
    1. Загрузка датасета
    2. Вывод статистики классов
    3. Очистка данных (удаление примеров с длиной != 64)
    4. Разбиение на train/test
    5. Создание и обучение модели
    6. Оценка качества
    7. Сохранение модели
    """
    # ----------------------------
    # ЗАГРУЗКА ДАННЫХ
    # ----------------------------
    X, y = load_dataset("X.npy", "y.npy")
    
    print("исходные классы:", Counter(y))
    print(f"Загружено примеров: {len(X)}")
    
    # ----------------------------
    # ОЧИСТКА ДАННЫХ
    # ----------------------------
    X, y = clean_dataset(X, y)
    print(f"После очистки: {len(X)} примеров")
    
    # ----------------------------
    # РАЗБИЕНИЕ НА TRAIN / TEST
    # ----------------------------
    X_train, X_test, y_train, y_test = split_dataset(X, y)
    
    print(f"\nОбучающая выборка: {len(X_train)}")
    print(f"Тестовая выборка: {len(X_test)}")
    
    # ----------------------------
    # СОЗДАНИЕ И ОБУЧЕНИЕ МОДЕЛИ
    # ----------------------------
    model = create_model()
    train_model(model, X_train, y_train)
    
    # ----------------------------
    # ОЦЕНКА КАЧЕСТВА
    # ----------------------------
    results = evaluate_model(model, X_test, y_test)
    
    print(f"\nТочность (Accuracy): {results['accuracy']:.4f}")
    print("\nОтчёт по классификации:\n")
    print(results['report'])
    
    # ----------------------------
    # СОХРАНЕНИЕ МОДЕЛИ
    # ----------------------------
    save_model(model)


if __name__ == "__main__":
    main()