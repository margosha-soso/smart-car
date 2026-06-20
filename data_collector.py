import cv2
import time
import mediapipe as mp
import numpy as np
import os
import logging
from pathlib import Path
from collections import Counter

#------------------------------------------------------------------------------------------------
# CONFIG настройки(переменные, которые можно динамично и удобно менять)

dataset_X_path = "X.npy"
dataset_y_path = "y.npy"

camera_width = 640
camera_height = 480

save_interval = 20 # для сохранения данных пачками
time_interval = 1 # раз в сколько секунд сохраняем

max_samples_per_class = 2000

pause_key = ord("p")

class_names = {
    ord('f'): "forward",
    ord('b'): "back",
    ord('l'): "left",
    ord('r'): "right",
    ord('s'): "stop",
    ord('g'): "no gesture"
}
#----------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------
# НАСТРОЙКА ЛОГОВ
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
#-----------------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------------
# DATASET настройка
# создает или загружает уже существующий датасет - на выходе 2 списка( названия меток и нормализированные координаты - если датасет уже был до этого)
def load_dataset():
    """
    Загружает существующий датасет или создает новый.
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

    np.save(dataset_X_path, np.array(features))
    np.save(dataset_y_path, np.array(labels))

    logging.info("Датасет сохранен")
#-----------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------
# НОРМАЛИЗАЦИЯ КООРДИНАТ

def normalize_landmarks(landmarks):

    if len(landmarks) != 21:
        return None

    wrist = landmarks[0]
    middle_mcp = landmarks[9]

    scale = np.sqrt(
        (middle_mcp.x - wrist.x) ** 2 +
        (middle_mcp.y - wrist.y) ** 2 +
        (middle_mcp.z - wrist.z) ** 2
    )

    if scale == 0:
        scale = 1

    normalized = []

    for lm in landmarks:

        normalized.extend([
            (lm.x - wrist.x) / scale,
            (lm.y - wrist.y) / scale,
            (lm.z - wrist.z) / scale
        ])

    return normalized
#------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------
# НАСТРОЙКА КАМЕРЫ

def initialize_camera():

    camera = cv2.VideoCapture(0)

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, camera_width)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_height)

    if not camera.isOpened():
        raise RuntimeError("Не удалось открыть камеру")

    return camera
#--------------------------------------------------------------------------------------------


def main():

    features, labels = load_dataset()

    # с помощью встроенной библиотеки считаем сколько уже есть данных
    label_counts = Counter(labels)

    # жест в данный момент
    current_label = None

    last_capture_time = 0
    save_counter = 0

    camera = initialize_camera()

    # создаем обьекты класса для работы с точками руки
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils

    # находим на камере руку(если уверенность к принадлежности к классу<70)
    hands = mp_hands.Hands(
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )

    logging.info("Управление:")
    logging.info("f - forward")
    logging.info("b - back")
    logging.info("l - left")
    logging.info("r - right")
    logging.info("s - stop")
    logging.info("n - pause")
    logging.info("q - quit")

    try:
        while True:

            success, frame = camera.read()

            if not success:
                logging.warning("Не удалось получить кадр")
                continue
            # cv2 использует BGR, a mediapipe RGB, для этого преобразовываем
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            result = hands.process(frame_rgb)

            # проверяем нашла ли библиотека mediapipe хоть 1 руку на изображении
            if result.multi_hand_landmarks:

                for hand_landmarks, handedness in zip(
                        result.multi_hand_landmarks,
                        result.multi_handedness
                ):

                    hand_label = handedness.classification[0].label

                    #  библиотека рисует на камере изображение руки
                    mp_draw.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS
                    )

                    current_time = time.time()

                    # проверяем достаточно ли прошло времени с последнего сохранения
                    enough_time_passed = (
                        current_time - last_capture_time
                        > time_interval
                    )

                    # проверка на выбор класса и колличество снимков
                    class_limit_not_reached = (
                        current_label is not None
                        and
                        label_counts[current_label]
                        < max_samples_per_class
                    )

                    if enough_time_passed and class_limit_not_reached:

                        landmarks_vector = normalize_landmarks(
                            hand_landmarks.landmark
                        )
                        if landmarks_vector is None:
                            continue

                        # если точки существуют и их длинна ровно 64(63 точки руки + 1 определение правая или левая -
                        # фильтр для того чтобы данные были одинаковые и без ошибок)
                        if len(landmarks_vector) != 63:
                            continue

                        is_right = 1 if hand_label == "Right" else 0
                        # добавляет в конец списка нормализированных координат определение правая или левая рука
                        landmarks_vector.append(is_right)

                        if len(landmarks_vector) != 64:
                            continue

                        features.append(landmarks_vector)
                        labels.append(current_label)
                        label_counts[current_label] += 1

                        last_capture_time = current_time
                        save_counter += 1

                        logging.info(
                            f"{current_label}: "
                            f"{label_counts[current_label]}"
                            )

                    else:
                        logging.warning("Кадр пропущен: не все точки руки видны камере")

                        # Автосохранение
                        if save_counter >= save_interval:

                            save_dataset(features, labels)

                            save_counter = 0

            key = cv2.waitKey(1) & 0xFF

            # переменная key определяет какая буква в англ раскладке сейчас нажата, а далее в заранее определеном классе class_names ищет совпадения
            if key in class_names:

                current_label = class_names[key]
                logging.info(f"Текущий сигнал: {current_label}")

            elif key == pause_key:

                current_label = None
                logging.info("запись остановлена")

            elif key == ord('q'):
                break
            # добавляем текст на камеру
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

        save_dataset(features, labels)
        camera.release()
        cv2.destroyAllWindows()
        logging.info("Программа завершена")

# программа запустится, если данный файл открыт как основной
if __name__ == "__main__":
    main()