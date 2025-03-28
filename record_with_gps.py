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

parser = argparse.ArgumentParser()
parser.add_argument('--duration', type=int, default=60)
parser.add_argument('--output', type=str, default=None)
args = parser.parse_args()

output_path = args.output or f"./logs/record_{datetime.now().strftime('%m%d%H%M')}.gpx"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

ser = serial.Serial('/dev/serial0', baudrate=9600, timeout=1)
start_time = time.time()
points = []

while time.time() - start_time < args.duration:
    line = ser.readline().decode(errors='ignore')
    if line.startswith('$GPRMC'):
        parsed = parse_nmea_gprmc(line)
        if parsed:
            timestamp, lat, lon, speed = parsed
            pt = f'<trkpt lat="{lat:.6f}" lon="{lon:.6f}"><time>{timestamp}</time><speed>{speed:.2f}</speed></trkpt>'
            points.append(pt)

with open(output_path, 'w') as f:
    f.write(generate_gpx_header() + '\n')
    f.write('\n'.join(points))
    f.write('\n' + generate_gpx_footer())

print(f"✅ 已儲存 GPX：{output_path}")