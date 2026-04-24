# lidar_manager.py
import threading
import time
from rplidar import RPLidar

PORT = 'COM3'
lidar = None
latest_scan = []
thread_started = False
lock = threading.Lock()

def get_lidar_instance():
    global lidar
    if lidar is None:
        lidar = RPLidar(PORT)
    return lidar

def read_lidar():
    global latest_scan
    try:
        lidar = get_lidar_instance()
        for scan in lidar.iter_scans(max_buf_meas=200):
            with lock:
                latest_scan = [(angle, distance) for (_, angle, distance) in scan if distance > 0]
            time.sleep(0.01)
    except Exception as e:
        print("🔴 LIDAR okuma hatası:", e)
    finally:
        if lidar:
            lidar.stop()
            lidar.disconnect()

def start_lidar_thread():
    global thread_started
    if not thread_started:
        t = threading.Thread(target=read_lidar, daemon=True)
        t.start()
        thread_started = True

def get_latest_scan():
    with lock:
        return latest_scan.copy()
