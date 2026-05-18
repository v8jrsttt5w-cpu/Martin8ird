# capture_douyin.py - screenshot抖音 page with scrolling
import time
import os
import pyautogui
import mss
from PIL import Image
from datetime import datetime

SAVE_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SAVE_DIR, exist_ok=True)

print("[capture] Starting in 3 seconds. Switch to Douyin app NOW...")
time.sleep(3)

for i in range(6):
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        img = sct.grab(monitor)
        png = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")
        # 不缩放，高质JPEG
        path = os.path.join(SAVE_DIR, f"douyin_{i+1:02d}.jpg")
        png.save(path, format="JPEG", quality=95)
        size_mb = os.path.getsize(path) / 1024 / 1024
        print(f"[capture] {i+1}/6 saved: {path} ({size_mb:.1f}MB)")

    if i < 5:
        pyautogui.scroll(-5)
        time.sleep(2)

print(f"[capture] Done. 6 PNG screenshots in: {SAVE_DIR}")
