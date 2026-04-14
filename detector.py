import cv2
from ultralytics import YOLO
import winsound
from logger import log_data
from risk_engine import calculate_risk

# Load YOLO model
model = YOLO("yolov8n.pt")

# Important objects
IMPORTANT_OBJECTS = ["person", "cell phone", "laptop"]

def run_detection():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Camera not accessible")
        return

    last_alert = ""

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to grab frame")
            break

        frame = frame.copy()
        detected_objects = set()

        # YOLO detection
        results = model(frame, stream=True)

        for r in results:
            if r.boxes is None:
                continue

            for box in r.boxes:
                cls_id = int(box.cls[0])
                label = model.names[cls_id]
                conf = float(box.conf[0])

                if label in IMPORTANT_OBJECTS:
                    detected_objects.add(label)

                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    # Draw object box (green initially)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    # Show label
                    cv2.putText(frame, f"{label} {conf:.2f}",
                                (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.8, (0, 255, 0), 2)

        # ===== RISK CALCULATION =====
        risk = calculate_risk(list(detected_objects))

        # ===== LOGGING =====
        log_data(list(detected_objects), risk)

        # ===== COLOR BASED ON RISK =====
        if risk == "HIGH":
            color = (0, 0, 255)      # Red
        elif risk == "MEDIUM":
            color = (0, 255, 255)    # Yellow
        else:
            color = (0, 255, 0)      # Green

        # ===== SCREEN BORDER =====
        h, w, _ = frame.shape
        cv2.rectangle(frame, (0, 0), (w, h), color, 10)

        # ===== RISK TEXT =====
        cv2.putText(frame, f"RISK LEVEL: {risk}", (30, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 4)

        # ===== SMART ALERT TEXT =====
        if risk == "HIGH":
            alert_text = "🚨 HIGH THREAT!"
        elif risk == "MEDIUM":
            alert_text = "⚠️ SUSPICIOUS ACTIVITY"
        else:
            alert_text = "✅ SAFE"

        cv2.putText(frame, alert_text, (30, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)

        # ===== SOUND ALERT =====
        if risk == "HIGH" and last_alert != "HIGH":
            winsound.Beep(1000, 500)
            last_alert = "HIGH"

        if risk != "HIGH":
            last_alert = ""

        # ===== STATUS TEXT =====
        cv2.putText(frame, "AI SURVEILLANCE RUNNING", (30, 220),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

        # ===== DISPLAY =====
        cv2.imshow("AI Surveillance System", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_detection()