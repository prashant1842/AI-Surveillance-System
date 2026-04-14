import subprocess

def scan_wifi():
    devices = []

    try:
        result = subprocess.check_output(
            "netsh wlan show networks", shell=True
        ).decode(errors="ignore")

        lines = result.split("\n")

        for line in lines:
            if "SSID" in line:
                parts = line.split(":")
                if len(parts) > 1:
                    name = parts[1].strip()
                    if name and name not in devices:
                        devices.append(name)

    except Exception as e:
        print("WiFi Scan Error:", e)

    return devices