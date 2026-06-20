import cv2
import numpy as np
import joblib
import mediapipe as mp
from collections import deque, Counter
import time
import  warnings
warnings.filterwarnings("ignore")
# =========================
# 1. LOAD MODEL
# =========================369

model = joblib.load("gesture_model.pkl")

# =========================
# 2. MEDIAPIPE SETUP
# =========================

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils

# =========================
# 3. SETTINGS
# =========================

CONF_THRESHOLD = 0.75
STABLE_FRAMES = 7
NO_HAND_TIMEOUT = 0.6

# =========================
# 4. STATE MEMORY (ВАЖНОЕ УЛУЧШЕНИЕ)
# =========================

buffer = deque(maxlen=STABLE_FRAMES)
last_hand_time = time.time()

# 👉 новая фича: запоминание последнего валидного состояния
last_good_features = None

# =========================
# 5. FEATURE BUILDER (ДОЛЖЕН СОВПАДАТЬ С TRAIN.PY)
# =========================

def get_features(hand_landmarks, hand_label):
    data = []

    # 63 landmarks (21 * 3)
    for lm in hand_landmarks.landmark:
        data.extend([lm.x, lm.y, lm.z])

    # +1 feature (hand side)
    is_right = 1 if hand_label == "Right" else 0
    data.append(is_right)

    return np.array(data)


def normalize(features):
    arr = np.array(features, dtype=np.float32)

    coords = arr[:63]
    is_right = arr[63]

    coords = coords.reshape(21,3)

    wrist = coords[0]
    middle_mcp = coords[9]

    scale = np.linalg.norm(middle_mcp - wrist)
    if scale == 0:
        scale = 1.0

    coords = (coords - wrist) / scale

    coords = coords.flatten()

    return np.append(coords, is_right)



# =========================
# 6. CAMERA
# =========================

cap = cv2.VideoCapture(0)

# =========================
# 7. MAIN LOOP
# =========================

while True:
    ret, frame = cap.read()
    if not ret:
        break

    #frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = hands.process(rgb)

    command = "STOP"

    # =========================
    # HAND DETECTION
    # =========================

    if result.multi_hand_landmarks:

        last_hand_time = time.time()

        for hand_landmarks, handedness in zip(
            result.multi_hand_landmarks,
            result.multi_handedness
        ):

            hand_label = handedness.classification[0].label

            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            # =========================
            # FEATURE EXTRACTION
            # =========================

            features = get_features(hand_landmarks, hand_label)
            print("длина features:", len(features))
            # =========================
            # LAST GOOD FEATURES LOGIC (ВОТ ОНА)
            # =========================

            if len(features) == 64:
                features = normalize(features)
            else:
                continue


            # =========================
            # MODEL PREDICTION
            # =========================

            probs = model.predict_proba([features])[0]

            idx = np.argmax(probs)
            confidence = probs[idx]
            pred_class = model.classes_[idx]

            print("предсказание моели:", pred_class, "conf:", confidence)

            # =========================
            # CONFIDENCE FILTER
            # =========================

            if confidence < CONF_THRESHOLD:
                pred_class = "STOP"

            # =========================
            # STABILITY FILTER
            # =========================

            buffer.append(pred_class)

            command = Counter(buffer).most_common(1)[0][0]

    else:
        # =========================
        # NO HAND SAFETY STOP
        # =========================

        if time.time() - last_hand_time > NO_HAND_TIMEOUT:
            buffer.clear()
            last_good_features = None  # сброс памяти
            command = "STOP"

    # =========================
    # UI
    # =========================

    color = (0, 255, 0) if command != "STOP" else (0, 0, 255)

    cv2.putText(
        frame,
        f"COMMAND: {command}",
        (10, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        color,
        2
    )

    cv2.imshow("PRO Gesture Control v2", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
