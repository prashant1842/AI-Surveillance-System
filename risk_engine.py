from logger import log_data

def calculate_risk(detected_data):

    # Convert to set
    detected_data = set(detected_data)

    # 🔥 RULES

    # Camera + phone → suspicious
    if "person" in detected_data and "cell phone" in detected_data:
        return "HIGH"

    # Unknown wireless devices
    elif "wifi_device_1" in detected_data or "bt_device_1" in detected_data:
        return "HIGH"

    elif "person" in detected_data:
        return "MEDIUM"

    elif "cell phone" in detected_data:
        return "LOW"

    else:
        return "SAFE"