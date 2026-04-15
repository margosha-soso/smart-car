import cv2
import time
import mediapipe as mp
import numpy as np

cap = cv2.VideoCapture(0) # подключаемся к видеопотоку(0 - встроенная камера)
cap.set(3, 640)
cap.set(4, 480)

X = [] # координаты руки
y = [] # метки label

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils # сокращенное название модуля рисования

hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
) # создание объекта класса, если уверенность к принадлежности к классу<70%, игнорируем

label = "None" # сигналы записываются только если они выбраны на клавиатуре

# фильтрация по времени
last_time = 0
time_interval = 0.4

print(
    "Нажмите на клавиатуре для записи:"
    "f - сигнал вперёд "
    "s - стоп "
    "l - лево "
    "r - право "
    "n - none "
    "q - выйти и сохранить результаты "
)

frame_count = 0

# нормализация руки(делаем руку независимой от положения и масштаба)
def normalize_landmarks(landmarks):
    coords = []
    # берем точку запястья как центр
    base_x = landmarks[0].x
    base_y = landmarks[0].y
    # считаем где пальцы относительно запястья
    for lm in landmarks:
        coords.append(lm.x - base_x)
        coords.append(lm.y - base_y)
    return coords

# баланс классов
label_counts = {
    "forward": 0,
    "back": 0,
    "left": 0,
    "right": 0
}
max_counts_class = 300 # максимальное кол-во примеров на 1 сигнал

while True:
    ret, frame = cap.read() # ret - успешно ли подключена камера, frame - изображение
    frame_count += 1
    if not ret:
        break
    if frame_count % 2 != 0:
        continue
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # mediapipe работает с RGB снимками
    result = hands.process(frame_rgb)

    # проверка обнаружения руки
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
            )
            # фильтрация по времени
            current_time =  time.time()
            if current_time - last_time > time_interval:
                data = normalize_landmarks(hand_landmarks.landmark)
                if label != 'None' and label_counts.get(label, 0) < max_counts_class:
                    X.append(data)
                    y.append(label)

                    label_counts[label] += 1
                    last_time = current_time

                    print('Сохранено:', label, label_counts[label])

# управление клавиатурой
    # клавиша, которая нажата
    key = cv2.waitKey(1) & 0xFF

    if key == ord('f'):
       label = "forward"
       print("сигнал: вперед")

    elif key == ord('s'):
        label = "stop"
        print("сигнал: стоп")

    elif key == ord('l'):
      label = "left"
      print("сигнал: лево руля")

    elif key == ord('r'):
      label = "right"
      print("сигнал: право руля")

    elif key == ord('n'):
      label = "none"
      print("сигнал: пауза")

    elif key == ord('q'):
       break
    # UI
    cv2.putText(frame, f"Сигнал: {label}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
    cv2.imshow("мама и папа никогда не верили в меня", frame)

# Сохранение

X = np.array(X)
y = np.array(y)
np.save("X.npy", X)
np.save("y.npy", y)

cap.release()
cv2.destroyAllWindows()