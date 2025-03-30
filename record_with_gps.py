# Version: v2 | Generated: 2025-03-30 17:19:48

import serial
import time
import wave
import os
import threading
from datetime import datetime

# ---------- Config ----------
LOG_DIR = "logs"
SAMPLE_RATE = 44100
CHANNELS = 1
WIDTH = 2  # bytes (16-bit)
DEVICE = "plughw:0,0"  # Based on arecord -L
SERIAL_PORT = "/dev/serial0"
DURATION_SECONDS = 60

# ---------- GPX Handling ----------
gpx_header_template = '<?xml version="1.0" encoding="UTF-8"?>\n' + \
'<gpx version="1.1" creator="record_with_gps.py" xmlns="http://www.topografix.com/GPX/1/1">\n' + \
'  <trk>\n' + \
'    <name>{}</name>\n' + \
'    <trkseg>\n'

gpx_footer = '    </trkseg>\n  </trk>\n</gpx>\n'


def parse_nmea_latlon(lat_str, lat_dir, lon_str, lon_dir):
    lat = float(lat_str[:2]) + float(lat_str[2:]) / 60
    lon = float(lon_str[:3]) + float(lon_str[3:]) / 60
    if lat_dir == 'S':
        lat = -lat
    if lon_dir == 'W':
        lon = -lon
    return lat, lon


def parse_gga(nmea_line):
    try:
        parts = nmea_line.split(',')
        if parts[0].endswith("GGA") and parts[6] != '0':
            lat, lon, alt, sats = parse_nmea_latlon(parts[2], parts[3], parts[4], parts[5])
            alt = float(parts[9])
            sats = int(parts[7])
            return lat, lon, alt, sats
    except Exception:
        pass
    return None


def parse_rmc(nmea_line):
    try:
        parts = nmea_line.split(',')
        if parts[0].endswith("RMC") and parts[2] == 'A':
            speed = float(parts[7]) * 0.514444
            return speed
    except Exception:
        pass
    return None


def wait_for_gps_fix():
    print("📡 等待 GPS fix（最高 60 秒）...")
    try:
        with serial.Serial(SERIAL_PORT, 9600, timeout=1) as ser:
            for _ in range(60):
                line = ser.readline().decode(errors='ignore').strip()
                if line.startswith("$GPGGA"):
                    if parse_gga(line):
                        print("✅ GPS fix 成功！")
                        return
                time.sleep(1)
    except Exception as e:
        print(f"❌ GPS 初始化失敗：{e}")
        raise
    raise TimeoutError("超過 60 秒仍無 GPS fix")


def gps_logger(gpx_path, duration):
    print("🛰 開始記錄 GPX")
    with open(gpx_path, 'w') as gpx_file:
        gpx_file.write(gpx_header_template.format(os.path.basename(gpx_path)))
        with serial.Serial(SERIAL_PORT, 9600, timeout=1) as ser:
            start_time = time.time()
            current_speed = 0.0
            while time.time() - start_time < duration:
                line = ser.readline().decode(errors='ignore').strip()
                if line.startswith("$GPGGA"):
                    data = parse_gga(line)
                    if data:
                        lat, lon, alt, sats = data
                        timestamp = datetime.utcnow().isoformat() + 'Z'
                        gpx_file.write(f'      <trkpt lat="{lat}" lon="{lon}"><ele>{alt}</ele><time>{timestamp}</time></trkpt>\n')
                        elapsed = int(time.time() - start_time)
                        print(f"🕒 {elapsed:>2} / {duration} 秒｜📍 {lat:.5f}, {lon:.5f}｜⛰️ {alt:.1f} m｜📶 衛星 {sats}")
                elif line.startswith("$GPRMC"):
                    speed = parse_rmc(line)
                    if speed is not None:
                        current_speed = speed
                time.sleep(0.2)
        gpx_file.write(gpx_footer)
    print("🛰 GPX 完成")


def record_audio(wav_path, duration):
    print(f"🎙 開始錄音 {duration} 秒...")
    os.system(f"arecord -D {DEVICE} -f S16_LE -r {SAMPLE_RATE} -c {CHANNELS} {wav_path} -d {duration}")


def main_loop():
    os.makedirs(LOG_DIR, exist_ok=True)
    while True:
        try:
            wait_for_gps_fix()
            now = datetime.now().strftime("%m%d_%H%M%S")
            filename_base = f"record_{now}"
            wav_path = os.path.join(LOG_DIR, f"{filename_base}.wav")
            gpx_path = os.path.join(LOG_DIR, f"{filename_base}.gpx")

            print("🟢 開始錄音與 GPS 紀錄...")
            gps_thread = threading.Thread(target=gps_logger, args=(gpx_path, DURATION_SECONDS))
            gps_thread.start()
            record_audio(wav_path, DURATION_SECONDS)
            gps_thread.join()
            print(f"✅ 已完成錄音與 GPX：{filename_base}\n")

        except Exception as e:
            print(f"❌ 發生錯誤：{e}")
            time.sleep(5)


if __name__ == '__main__':
    main_loop()
