<<<<<<< HEAD
"""
@defgroup gesture_control Gesture Control System
@brief Система управления роботом жестами с использованием компьютерного зрения и машинного обучения.
@details
Этот модуль реализует полный пайплайн:
- Захват видео с веб-камеры
- Детекция руки с помощью MediaPipe
- Извлечение и нормализация признаков
- Классификация жестов обученной моделью
- Отправка команд на робота через Bluetooth (Serial)
"""

=======
>>>>>>> 3728a9054311c79fd686de47af894c899a97d260
import cv2
import numpy as np
import joblib
import mediapipe as mp
import serial
import time
import logging
<<<<<<< HEAD
import warnings

from collections import deque, Counter

# Подавляем предупреждения для чистоты вывода
warnings.filterwarnings("ignore")


# ============================================================
# CONFIG
# ============================================================

MODEL_PATH = "gesture_model.pkl"                # Путь к обученной модели
SERIAL_PORT = "COM7"                           # COM-порт для Bluetooth-связи
BAUD_RATE = 115200                             # Скорость передачи данных

CONF_THRESHOLD = 0.80                          # Минимальная уверенность для принятия жеста
STABLE_FRAMES = 3                              # Количество кадров для сглаживания
NO_HAND_TIMEOUT = 0.5                          # Время ожидания потери руки (сек)

COMMAND_COOLDOWN = 0.25                         # Задержка между отправками команд (сек)
=======
import  warnings
warnings.filterwarnings("ignore")

from collections import deque, Counter


# ============================================================
# CONFIG
# ============================================================

MODEL_PATH = "gesture_model.pkl"

SERIAL_PORT = "COM4"
BAUD_RATE = 115200

CONF_THRESHOLD = 0.80

STABLE_FRAMES = 3
NO_HAND_TIMEOUT = 0.5

COMMAND_COOLDOWN = 0.25
>>>>>>> 3728a9054311c79fd686de47af894c899a97d260

GESTURE_TO_ROBOT = {
    "forward": "F",
    "back": "B",
    "left": "L",
    "right": "R",
    "stop": "S"
}
<<<<<<< HEAD
"""
@var GESTURE_TO_ROBOT
@brief Словарь для сопоставления названий жестов с командами для робота.
"""
=======
>>>>>>> 3728a9054311c79fd686de47af894c899a97d260


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s"
)
<<<<<<< HEAD
"""
@brief Настройка логирования с выводом времени.
"""
=======
>>>>>>> 3728a9054311c79fd686de47af894c899a97d260


# ============================================================
# ROBOT CONTROLLER (BLUETOOTH / SERIAL)
# ============================================================

class RobotController:
<<<<<<< HEAD
    """
    @brief Класс для управления роботом по последовательному порту (Bluetooth).
    @details
    Обеспечивает подключение к роботу, отправку команд и экстренную остановку.
    Реализует защиту от дублирования команд.
    """

    def __init__(self, port, baud):
        """
        @brief Конструктор класса RobotController.
        @param port       COM-порт для подключения (например, "COM7").
        @param baud       Скорость передачи данных (бод).
        """
        self.port = port
        self.baud = baud
        self.serial = None
=======
    def __init__(self, port, baud):
        self.port = port
        self.baud = baud
        self.serial = None

>>>>>>> 3728a9054311c79fd686de47af894c899a97d260
        self.last_command = None
        self.last_send_time = 0

    def connect(self):
<<<<<<< HEAD
        """
        @brief Устанавливает соединение с роботом по последовательному порту.
        @details Открывает порт, ждёт 2 секунды для инициализации и отправляет команду "S" (стоп).
        """
        self.serial = serial.Serial(self.port, self.baud, timeout=1)
        time.sleep(2)
        logging.info(f"Connected to robot on {self.port}")
        self.send("S")

    def send(self, command):
        """
        @brief Отправляет команду роботу.
        @details
        Команда не отправляется, если она совпадает с предыдущей (защита от спама).
        @param command   Одиночный символ команды ('F', 'B', 'L', 'R', 'S').
        """
=======
        self.serial = serial.Serial(self.port, self.baud, timeout=1)
        time.sleep(2)
        logging.info(f"Connected to robot on {self.port}")

        self.send("S")

    def send(self, command):
>>>>>>> 3728a9054311c79fd686de47af894c899a97d260
        if self.serial is None:
            return

        now = time.time()

<<<<<<< HEAD
        # Защита от повторной отправки той же команды
=======
        # антиспам
>>>>>>> 3728a9054311c79fd686de47af894c899a97d260
        if command == self.last_command:
            return

        try:
            self.serial.write((command + "\n").encode())
<<<<<<< HEAD
            logging.info(f"-> ROBOT: {command}")
=======

            logging.info(f"-> ROBOT: {command}")

>>>>>>> 3728a9054311c79fd686de47af894c899a97d260
            self.last_command = command
            self.last_send_time = now

        except Exception as e:
            logging.error(f"Serial send error: {e}")

    def emergency_stop(self):
<<<<<<< HEAD
        """
        @brief Отправляет команду экстренной остановки.
        """
        self.send("S")

    def close(self):
        """
        @brief Закрывает соединение с роботом.
        @details
        Отправляет команду стоп и закрывает последовательный порт.
        """
        self.emergency_stop()
        if self.serial:
            self.serial.close()
=======
        self.send("S")

    def close(self):
        self.emergency_stop()

        if self.serial:
            self.serial.close()

>>>>>>> 3728a9054311c79fd686de47af894c899a97d260
        logging.info("Connection closed")


# ============================================================
# FEATURE ENGINEERING (MUST MATCH TRAINING)
# ============================================================

def extract_features(hand_landmarks, label):
<<<<<<< HEAD
    """
    @brief Извлекает сырые признаки из данных MediaPipe.
    @param hand_landmarks   Объект hand_landmarks от MediaPipe.
    @param label            Строка "Left" или "Right" — обозначение руки.
    @return                 Вектор признаков размером 64 (21 точка * 3 координаты + 1 флаг руки).
    """
=======
>>>>>>> 3728a9054311c79fd686de47af894c899a97d260
    data = []

    for lm in hand_landmarks.landmark:
        data.extend([lm.x, lm.y, lm.z])

    data.append(1 if label == "Right" else 0)

    return np.array(data, dtype=np.float32)


def normalize(features):
<<<<<<< HEAD
    """
    @brief Нормализует признаки, делая их инвариантными к положению руки в кадре.
    @details
    - Смещение относительно запястья (точка 0)
    - Масштабирование по расстоянию от запястья до основания среднего пальца (точка 9)
    @param features     Сырой вектор признаков (64 элемента).
    @return             Нормализованный вектор признаков (64 элемента).
    """
=======
>>>>>>> 3728a9054311c79fd686de47af894c899a97d260
    coords = features[:63].reshape(21, 3)

    wrist = coords[0]
    middle = coords[9]

    scale = np.linalg.norm(middle - wrist)

    if scale < 1e-6:
        scale = 1.0

    coords = (coords - wrist) / scale

    return np.append(coords.flatten(), features[63])


# ============================================================
# GESTURE AI ENGINE
# ============================================================

class GestureAI:
<<<<<<< HEAD
    """
    @brief Класс для распознавания жестов с использованием обученной модели.
    @details
    Загружает модель, выполняет предсказания, применяет порог уверенности
    и сглаживает результаты по нескольким кадрам.
    """

    def __init__(self, model_path):
        """
        @brief Конструктор класса GestureAI.
        @param model_path   Путь к файлу обученной модели (.pkl).
        """
        self.model = joblib.load(model_path)
        self.buffer = deque(maxlen=STABLE_FRAMES)

    def predict(self, features):
        """
        @brief Выполняет предсказание жеста по вектору признаков.
        @details
        1. Получает вероятности классов от модели.
        2. Выбирает класс с максимальной вероятностью.
        3. Если уверенность ниже порога, возвращает "STOP".
        4. Добавляет результат в буфер и возвращает наиболее частый жест за последние кадры.
        @param features     Нормализованный вектор признаков (64 элемента).
        @return             Кортеж: (название жеста, уверенность).
        """
=======
    def __init__(self, model_path):
        self.model = joblib.load(model_path)

        self.buffer = deque(maxlen=STABLE_FRAMES)

    def predict(self, features):
>>>>>>> 3728a9054311c79fd686de47af894c899a97d260
        probs = self.model.predict_proba([features])[0]

        idx = np.argmax(probs)
        confidence = probs[idx]
        gesture = self.model.classes_[idx]

<<<<<<< HEAD
        # Отладочная печать
=======
>>>>>>> 3728a9054311c79fd686de47af894c899a97d260
        print("RAW:", gesture, confidence)

        if confidence < CONF_THRESHOLD:
            gesture = "STOP"

        self.buffer.append(gesture)

        stable = Counter(self.buffer).most_common(1)[0][0]

        print("RETURN:", stable)

        return stable, confidence


# ============================================================
# MAIN SYSTEM
# ============================================================

def main():
<<<<<<< HEAD
    """
    @brief Основная функция управления роботом жестами.
    @details
    Последовательность работы:
    1. Подключение к роботу (Bluetooth)
    2. Загрузка модели жестов
    3. Инициализация камеры и MediaPipe
    4. Основной цикл: захват кадра → детекция руки → предсказание жеста → отправка команды
    5. Обработка ошибок и безопасное завершение
    """
=======

>>>>>>> 3728a9054311c79fd686de47af894c899a97d260
    # ----------------------------
    # INIT ROBOT
    # ----------------------------
    robot = RobotController(SERIAL_PORT, BAUD_RATE)
    robot.connect()

    # ----------------------------
    # INIT AI
    # ----------------------------
    ai = GestureAI(MODEL_PATH)

    # ----------------------------
    # INIT CAMERA + MEDIAPIPE
    # ----------------------------
    mp_hands = mp.solutions.hands

    hands = mp_hands.Hands(
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )

    draw = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)

    last_hand_time = time.time()

    # ============================
    # MAIN LOOP
    # ============================
    try:
        while True:
<<<<<<< HEAD
=======

>>>>>>> 3728a9054311c79fd686de47af894c899a97d260
            ret, frame = cap.read()
            if not ret:
                break

<<<<<<< HEAD
            # Зеркальное отражение (опционально)
            # frame = cv2.flip(frame, 1)
=======
            #frame = cv2.flip(frame, 1)
>>>>>>> 3728a9054311c79fd686de47af894c899a97d260

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb)

            command = "S"
            confidence = 0.0

            # ----------------------------
            # HAND DETECTED
            # ----------------------------
            if result.multi_hand_landmarks:
<<<<<<< HEAD
=======

>>>>>>> 3728a9054311c79fd686de47af894c899a97d260
                last_hand_time = time.time()

                hand = result.multi_hand_landmarks[0]
                label = result.multi_handedness[0].classification[0].label

                draw.draw_landmarks(
                    frame,
                    hand,
                    mp_hands.HAND_CONNECTIONS
                )

                features = extract_features(hand, label)
                features = normalize(features)

                gesture, confidence = ai.predict(features)

                print("gesture", gesture)
                print("command=", GESTURE_TO_ROBOT)

                command = GESTURE_TO_ROBOT.get(gesture, "S")

            # ----------------------------
            # HAND LOST SAFETY
            # ----------------------------
            else:
                if time.time() - last_hand_time > NO_HAND_TIMEOUT:
                    ai.buffer.clear()
                    command = "S"

            # ----------------------------
            # SEND TO ROBOT
            # ----------------------------
            print("command=", command)
            robot.send(command)

            # ----------------------------
            # UI
            # ----------------------------
            color = (0, 255, 0) if command != "S" else (0, 0, 255)

            cv2.putText(
                frame,
                f"{command} | {confidence:.2f}",
                (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                color,
                2
            )

            cv2.imshow("Robot Gesture AI Control", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        logging.error(f"Critical error: {e}")
        robot.emergency_stop()

    finally:
        robot.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
<<<<<<< HEAD
    main()
=======
    main()
>>>>>>> 3728a9054311c79fd686de47af894c899a97d260
