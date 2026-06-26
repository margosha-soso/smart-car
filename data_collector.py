"""
@defgroup data_collector Data Collector
@brief Сбор и сохранение датасета жестов рук с веб-камеры.
@details
Этот модуль реализует сбор данных для обучения модели распознавания жестов.
Основные функции:
- Захват видео с веб-камеры
- Детекция руки с помощью MediaPipe
- Нормализация координат ключевых точек
- Сохранение признаков и меток в файлы .npy
- Управление сбором через клавиатуру
"""

import cv2
import time
import mediapipe as mp
import numpy as np
import os
import logging
from pathlib import Path
from collections import Counter


# ============================================================
# CONFIG
# ============================================================

dataset_X_path = "X.npy"          # Путь для сохранения признаков
dataset_y_path = "y.npy"          # Путь для сохранения меток

camera_width = 640                # Ширина кадра с камеры
camera_height = 480               # Высота кадра с камеры

save_interval = 20                # Количество примеров для пачки сохранения
time_interval = 1                 # Интервал между сохранениями (сек)

max_samples_per_class = 2000      # Максимальное количество примеров на класс

pause_key = ord("p")              # Клавиша паузы

class_names = {
    ord('f'): "forward",
    ord('b'): "back",
    ord('l'): "left",
    ord('r'): "right",
    ord('s'): "stop",
    ord('g'): "no gesture"
}
"""
@var class_names
@brief Словарь для сопоставления клавиш с названиями жестов.
"""


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
"""
@brief Настройка логирования с выводом времени и уровня.
"""


# ============================================================
# DATASET MANAGEMENT
# ============================================================

def load_dataset():
    """
    @brief Загружает существующий датасет или создаёт новый.
    @details
    Проверяет наличие файлов X.npy и y.npy.
    Если файлы существуют — загружает их.
    Если нет — создаёт пустые списки.
    @return Кортеж (features, labels) — списки признаков и меток.
    """
    if Path(dataset_X_path).exists() and Path(dataset_y_path).exists():
        features = list(np.load(dataset_X_path, allow_pickle=True))
        labels = list(np.load(dataset_y_path, allow_pickle=True))
        logging.info(f"Загружено {len(features)} примеров")
    else:
        features = []
        labels = []
        logging.info("Создан новый датасет")
    return features, labels


def save_dataset(features, labels):
    """
    @brief Сохраняет датасет в файлы .npy.
    @param features   Список векторов признаков.
    @param labels     Список меток классов.
    """
    np.save(dataset_X_path, np.array(features))
    np.save(dataset_y_path, np.array(labels))
    logging.info("Датасет сохранен")


# ============================================================
# FEATURE ENGINEERING
# ============================================================

def normalize_landmarks(landmarks):
    """
    @brief Нормализует координаты ключевых точек руки.
    @details
    - Запястье (точка 0) используется как центр координат.
    - Расстояние от запястья до основания среднего пальца (точка 9) используется как масштаб.
    - Нормализация делает признаки инвариантными к положению руки в кадре и расстоянию до камеры.
    @param landmarks   Список из 21 ключевой точки руки от MediaPipe.
    @return            Вектор из 63 нормализованных координат (21 точка * 3 координаты) или None, если входных точек не 21.
    """
    if len(landmarks) != 21:
        return None

    wrist = landmarks[0]
    middle_mcp = landmarks[9]

    # Вычисляем масштаб как расстояние от запястья до основания среднего пальца
    scale = np.sqrt(
        (middle_mcp.x - wrist.x) ** 2 +
        (middle_mcp.y - wrist.y) ** 2 +
        (middle_mcp.z - wrist.z) ** 2
    )

    if scale == 0:
        scale = 1  # Защита от деления на ноль

    normalized = []

    for lm in landmarks:
        normalized.extend([
            (lm.x - wrist.x) / scale,
            (lm.y - wrist.y) / scale,
            (lm.z - wrist.z) / scale
        ])

    return normalized


# ============================================================
# CAMERA MANAGEMENT
# ============================================================

def initialize_camera():
    """
    @brief Инициализирует веб-камеру и устанавливает разрешение.
    @details
    Открывает камеру с индексом 0 и устанавливает ширину и высоту кадра.
    @return Объект VideoCapture.
    @throws RuntimeError Если не удалось открыть камеру.
    """
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, camera_width)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_height)

    if not camera.isOpened():
        raise RuntimeError("Не удалось открыть камеру")

    return camera


# ============================================================
# MAIN FUNCTION
# ============================================================

def main():
    """
    @brief Основная функция сбора данных.
    @details
    Последовательность работы:
    1. Загрузка существующего датасета
    2. Инициализация камеры и MediaPipe
    3. Основной цикл:
       - Захват кадра
       - Детекция руки
       - Нормализация координат
       - Сохранение примеров при нажатии клавиши
    4. Автосохранение по достижении save_interval
    5. Сохранение датасета при завершении
    """
    # ----------------------------
    # ЗАГРУЗКА ДАТАСЕТА
    # ----------------------------
    features, labels = load_dataset()
    label_counts = Counter(labels)      # Счётчик примеров по классам

    current_label = None                # Текущий выбранный жест
    last_capture_time = 0               # Время последнего сохранения
    save_counter = 0                    # Счётчик сохранённых примеров с последней пачки

    # ----------------------------
    # ИНИЦИАЛИЗАЦИЯ КАМЕРЫ
    # ----------------------------
    camera = initialize_camera()

    # ----------------------------
    # ИНИЦИАЛИЗАЦИЯ MEDIAPIPE
    # ----------------------------
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils

    hands = mp_hands.Hands(
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )

    # ----------------------------
    # ВЫВОД УПРАВЛЕНИЯ
    # ----------------------------
    logging.info("Управление:")
    logging.info("f - forward")
    logging.info("b - back")
    logging.info("l - left")
    logging.info("r - right")
    logging.info("s - stop")
    logging.info("n - pause")
    logging.info("q - quit")

    # ============================
    # ОСНОВНОЙ ЦИКЛ
    # ============================
    try:
        while True:
            # ----------------------------
            # ЗАХВАТ КАДРА
            # ----------------------------
            success, frame = camera.read()
            if not success:
                logging.warning("Не удалось получить кадр")
                continue

            # Конвертация BGR → RGB для MediaPipe
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(frame_rgb)

            # ----------------------------
            # ДЕТЕКЦИЯ РУКИ
            # ----------------------------
            if result.multi_hand_landmarks:
                for hand_landmarks, handedness in zip(
                        result.multi_hand_landmarks,
                        result.multi_handedness
                ):
                    hand_label = handedness.classification[0].label

                    # Визуализация ключевых точек руки
                    mp_draw.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS
                    )

                    current_time = time.time()

                    # Проверка условий для сохранения
                    enough_time_passed = (
                        current_time - last_capture_time > time_interval
                    )

                    class_limit_not_reached = (
                        current_label is not None
                        and label_counts[current_label] < max_samples_per_class
                    )

                    # ----------------------------
                    # СОХРАНЕНИЕ ПРИМЕРА
                    # ----------------------------
                    if enough_time_passed and class_limit_not_reached:
                        landmarks_vector = normalize_landmarks(
                            hand_landmarks.landmark
                        )
                        if landmarks_vector is None:
                            continue

                        if len(landmarks_vector) != 63:
                            continue

                        # Добавляем флаг "правая/левая рука" (64-й параметр)
                        is_right = 1 if hand_label == "Right" else 0
                        landmarks_vector.append(is_right)

                        if len(landmarks_vector) != 64:
                            continue

                        features.append(landmarks_vector)
                        labels.append(current_label)
                        label_counts[current_label] += 1

                        last_capture_time = current_time
                        save_counter += 1

                        logging.info(
                            f"{current_label}: {label_counts[current_label]}"
                        )

                    else:
                        logging.warning(
                            "Кадр пропущен: не все точки руки видны камере"
                        )

                    # ----------------------------
                    # АВТОСОХРАНЕНИЕ ПАЧКАМИ
                    # ----------------------------
                    if save_counter >= save_interval:
                        save_dataset(features, labels)
                        save_counter = 0

            # ----------------------------
            # ОБРАБОТКА КЛАВИШ
            # ----------------------------
            key = cv2.waitKey(1) & 0xFF

            if key in class_names:
                current_label = class_names[key]
                logging.info(f"Текущий сигнал: {current_label}")

            elif key == pause_key:
                current_label = None
                logging.info("запись остановлена")

            elif key == ord('q'):
                break

            # ----------------------------
            # ОТОБРАЖЕНИЕ
            # ----------------------------
            cv2.putText(
                frame,
                f"Signal: {current_label}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 0, 255),
                2
            )

            cv2.imshow("Hand Dataset Collector", frame)

    finally:
        # ----------------------------
        # ЗАВЕРШЕНИЕ
        # ----------------------------
        save_dataset(features, labels)
        camera.release()
        cv2.destroyAllWindows()
        logging.info("Программа завершена")


# ============================================================
# ТОЧКА ВХОДА
# ============================================================

if __name__ == "__main__":
    main()