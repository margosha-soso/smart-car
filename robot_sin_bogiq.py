import cv2
import numpy as np
import joblib
import mediapipe as mp
import serial
import time
import logging
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

GESTURE_TO_ROBOT = {
    "forward": "F",
    "back": "B",
    "left": "L",
    "right": "R",
    "stop": "S"
}


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s"
)


# ============================================================
# ROBOT CONTROLLER (BLUETOOTH / SERIAL)
# ============================================================

class RobotController:
    def __init__(self, port, baud):
        self.port = port
        self.baud = baud
        self.serial = None

        self.last_command = None
        self.last_send_time = 0

    def connect(self):
        self.serial = serial.Serial(self.port, self.baud, timeout=1)
        time.sleep(2)
        logging.info(f"Connected to robot on {self.port}")

        self.send("S")

    def send(self, command):
        if self.serial is None:
            return

        now = time.time()

        # антиспам
        if command == self.last_command:
            return

        try:
            self.serial.write((command + "\n").encode())

            logging.info(f"-> ROBOT: {command}")

            self.last_command = command
            self.last_send_time = now

        except Exception as e:
            logging.error(f"Serial send error: {e}")

    def emergency_stop(self):
        self.send("S")

    def close(self):
        self.emergency_stop()

        if self.serial:
            self.serial.close()

        logging.info("Connection closed")


# ============================================================
# FEATURE ENGINEERING (MUST MATCH TRAINING)
# ============================================================

def extract_features(hand_landmarks, label):
    data = []

    for lm in hand_landmarks.landmark:
        data.extend([lm.x, lm.y, lm.z])

    data.append(1 if label == "Right" else 0)

    return np.array(data, dtype=np.float32)


def normalize(features):
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
    def __init__(self, model_path):
        self.model = joblib.load(model_path)

        self.buffer = deque(maxlen=STABLE_FRAMES)

    def predict(self, features):
        probs = self.model.predict_proba([features])[0]

        idx = np.argmax(probs)
        confidence = probs[idx]
        gesture = self.model.classes_[idx]

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

            ret, frame = cap.read()
            if not ret:
                break

            #frame = cv2.flip(frame, 1)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb)

            command = "S"
            confidence = 0.0

            # ----------------------------
            # HAND DETECTED
            # ----------------------------
            if result.multi_hand_landmarks:

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
    main()
