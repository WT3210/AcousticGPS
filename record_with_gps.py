import os
import time
import argparse
import serial
from datetime import datetime

def generate_gpx_header():
    return '''<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="AcousticGPS" xmlns="http://www.topografix.com/GPX/1/1">
  <trk><name>GPS Track</name><trkseg>'''

def generate_gpx_footer():
    return '''</trkseg></trk></gpx>'''

def parse_nmea_gprmc(nmea):
    parts = nmea.strip().split(',')
    if len(parts) < 12 or parts[2] != 'A':
        return None
    try:
        raw_time = parts[1]
        raw_date = parts[9]
        timestamp = datetime.strptime(raw_date + raw_time, '%d%m%y%H%M%S').isoformat() + 'Z'
        lat = float(parts[3][:2]) + float(parts[3][2:]) / 60.0
        if parts[4] == 'S':
            lat = -lat
        lon = float(parts[5][:3]) + float(parts[5][3:]) / 60.0
        if parts[6] == 'W':
            lon = -lon
        speed = float(parts[7]) * 0.514444  # knots to m/s
        return timestamp, lat, lon, speed
    except:
        return None

def parse_nmea_gpgga(nmea):
    parts = nmea.strip().split(',')
    if len(parts) < 15:
        return None
    try:
        altitude = float(parts[9])
        sat_count = int(parts[7])
        return altitude, sat_count
    except:
        return None

parser = argparse.ArgumentParser()
parser.add_argument('--duration', type=int, default=60)
parser.add_argument('--output', type=str, default=None)
args = parser.parse_args()

output_path = args.output or f"./logs/record_{datetime.now().strftime('%m%d%H%M')}.gpx"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

ser = serial.Serial('/dev/serial0', baudrate=9600, timeout=1)

print("📡 等待 GPS fix（最高 60 秒）...")
fix_acquired = False
fix_wait_start = time.time()
while time.time() - fix_wait_start < 60:
    line = ser.readline().decode(errors='ignore')
    if line.startswith('$GPRMC'):
        parsed = parse_nmea_gprmc(line)
        if parsed:
            fix_acquired = True
            print("✅ GPS fix 成功！開始紀錄...")
            break
if not fix_acquired:
    print("❌ GPS fix 逾時，取消 GPX 紀錄")
    exit()

start_time = time.time()
points = []
last_alt = None
last_sat = None
print("🔴 錄製中...")

while time.time() - start_time < args.duration:
    line = ser.readline().decode(errors='ignore')
    elapsed = int(time.time() - start_time)

    if line.startswith('$GPRMC'):
        parsed = parse_nmea_gprmc(line)
        if parsed:
            timestamp, lat, lon, speed = parsed
            pt = f'<trkpt lat="{lat:.6f}" lon="{lon:.6f}"><time>{timestamp}</time><speed>{speed:.2f}</speed></trkpt>'
            points.append(pt)

            print(f"🕐 秒數：{elapsed}s | 📍 {lat:.5f}, {lon:.5f} | 🚀 {speed:.2f} m/s", end='')
            if last_alt is not None and last_sat is not None:
                print(f" | ⛰ {last_alt:.1f} m | 📶 衛星：{last_sat}", end='')
            print()

    elif line.startswith('$GPGGA'):
        alt_sat = parse_nmea_gpgga(line)
        if alt_sat:
            last_alt, last_sat = alt_sat

if not points:
    print("⚠️ 沒有獲得任何 GPS 資料，GPX 將不儲存")
    exit()

with open(output_path, 'w') as f:
    f.write(generate_gpx_header() + '\n')
    f.write('\n'.join(points))
    f.write('\n' + generate_gpx_footer())

print(f"✅ 已儲存 GPX：{output_path}")