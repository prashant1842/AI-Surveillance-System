import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import streamlit as st
import cv2
from ultralytics import YOLO
import pandas as pd
import time
from datetime import datetime
import glob

from risk_engine import calculate_risk
from logger import log_data
from wifi_scanner import scan_wifi
from bluetooth_scanner import scan_bluetooth

# -------------------- CONFIG --------------------
st.set_page_config(page_title="AI Surveillance Dashboard", layout="wide")
st.title("🚨 AI Surveillance Dashboard")

# -------------------- SIDEBAR --------------------
st.sidebar.title("Navigation")
option = st.sidebar.radio(
    "Select Module",
    ["🎥 Camera Detection", "📡 WiFi Scanner", "📶 Bluetooth Scanner"]
)

# -------------------- MODEL --------------------
@st.cache_resource
def load_model():
    return YOLO("yolov8n.pt")

model = load_model()
IMPORTANT_OBJECTS = ["person", "cell phone", "laptop"]

# -------------------- SESSION --------------------
if "run" not in st.session_state:
    st.session_state.run = False

if "risk_history" not in st.session_state:
    st.session_state.risk_history = []

if "logs" not in st.session_state:
    st.session_state.logs = []

# =====================================================
# 🎥 CAMERA SECTION
# =====================================================
if option == "🎥 Camera Detection":

    st.header("🎥 Live Camera Detection")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("▶️ Start Camera"):
            st.session_state.run = True

    with col2:
        if st.button("⏹ Stop Camera"):
            st.session_state.run = False

    frame_placeholder = st.empty()
    risk_placeholder = st.empty()
    alert_placeholder = st.empty()
    chart_placeholder = st.empty()
    objects_placeholder = st.empty()

    if st.session_state.run:

        cap = cv2.VideoCapture(0)

        while st.session_state.run:

            ret, frame = cap.read()
            if not ret:
                st.error("Camera not accessible")
                break

            detected_objects = set()

            results = model(frame, conf=0.5, verbose=False)

            for r in results:
                if r.boxes is None:
                    continue

                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    label = model.names[cls_id]

                    if label in IMPORTANT_OBJECTS:
                        detected_objects.add(label)

                        x1, y1, x2, y2 = map(int, box.xyxy[0])

                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, label, (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # ---------------- RISK ----------------
            risk = calculate_risk(list(detected_objects))
            log_data(list(detected_objects), risk)

            timestamp = datetime.now().strftime("%H:%M:%S")

            st.session_state.logs.append({
                "Time": timestamp,
                "Objects": ", ".join(detected_objects),
                "Risk": risk
            })

            if len(st.session_state.logs) > 100:
                st.session_state.logs.pop(0)

            value = 0 if risk == "SAFE" else 1 if risk == "MEDIUM" else 2
            st.session_state.risk_history.append(value)

            if len(st.session_state.risk_history) > 50:
                st.session_state.risk_history.pop(0)

            # ---------------- SCREENSHOT ----------------
            if risk == "HIGH":
                os.makedirs("snapshots", exist_ok=True)
                filename = f"snapshots/{int(time.time())}.jpg"
                cv2.imwrite(filename, frame)

            # ---------------- UI ----------------
            risk_placeholder.markdown(f"## Risk Level: **{risk}**")

            if risk == "HIGH":
                alert_placeholder.error("🚨 HIGH RISK!")
                st.audio("https://www.soundjay.com/buttons/beep-01a.mp3")
            elif risk == "MEDIUM":
                alert_placeholder.warning("⚠️ Suspicious Activity")
            else:
                alert_placeholder.success("✅ Safe")

            objects_placeholder.info(
                f"Detected: {', '.join(detected_objects) if detected_objects else 'None'}"
            )

            df = pd.DataFrame(st.session_state.risk_history, columns=["Risk"])
            chart_placeholder.line_chart(df)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(frame, channels="RGB")

            time.sleep(0.03)

        cap.release()

    # ---------------- LOG TABLE ----------------
    if st.session_state.logs:
        st.subheader("📊 Recent Logs")
        df_logs = pd.DataFrame(st.session_state.logs)
        st.dataframe(df_logs)

        st.download_button("📥 Download Logs", df_logs.to_csv(index=False), "logs.csv")

    # ---------------- ANALYTICS ----------------
    if st.session_state.risk_history:
        st.subheader("📈 Risk Analytics")
        df = pd.DataFrame(st.session_state.risk_history, columns=["Risk"])
        st.bar_chart(df["Risk"].value_counts())

    # ---------------- SNAPSHOT VIEWER ----------------
    st.subheader("📸 Captured Alerts")
    images = glob.glob("snapshots/*.jpg")

    for img in images[-5:]:
        st.image(img, width=200)

# =====================================================
# 📡 WIFI SECTION
# =====================================================
elif option == "📡 WiFi Scanner":

    st.header("📡 WiFi Networks Nearby")

    if st.button("Scan WiFi"):
        with st.spinner("Scanning WiFi..."):
            devices = scan_wifi()

        if devices:
            for i, d in enumerate(devices):
                st.success(f"{i+1}. {d}")
        else:
            st.warning("No WiFi networks found")

# =====================================================
# 📶 BLUETOOTH SECTION
# =====================================================
elif option == "📶 Bluetooth Scanner":

    st.header("📶 Bluetooth Devices Nearby")

    if st.button("Scan Bluetooth"):
        with st.spinner("Scanning Bluetooth..."):
            devices = scan_bluetooth()

        if devices:
            for i, d in enumerate(devices):
                st.info(f"{i+1}. {d}")
        else:
            st.warning("No Bluetooth devices found")