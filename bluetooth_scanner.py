from bleak import BleakScanner
import asyncio

def scan_bluetooth():
    devices_list = []

    async def run_scan():
        devices = await BleakScanner.discover(timeout=5)
        for d in devices:
            name = d.name if d.name else "Unknown Device"
            devices_list.append(f"{name} ({d.address})")

    try:
        asyncio.run(run_scan())
    except Exception as e:
        print("Bluetooth Scan Error:", e)

    return devices_list