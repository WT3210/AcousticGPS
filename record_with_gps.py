
import os
import time
import threading
import subprocess
from datetime import datetime
import gpsd

output_dir = os.path.expanduser("~/AcousticRecorder/logs")
filename_prefix = datetime.now().strftime("record_%Y%m%d_%H%M%S")
wav_path = os.path.join(output_dir, filename_prefix + ".wav")
gpx_path = os.path.join(output_dir, filename_prefix + ".gpx")

def init_gpx():
    with open(gpx_path, 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<gpx version="1.1" creator="PiRecorder" xmlns="http://www.topografix.com/GPX/1/1">\n')
        f.write('  <trk><name>' + filename_prefix + '</name><trkseg>\n')

def append_gpx(lat, lon, ele, speed):
    now = datetime.utcnow().isoformat() + "Z"
    with open(gpx_path, 'a') as f:
        f.write('    <trkpt lat="{:.8f}" lon="{:.8f}">\n'.format(lat, lon))
        f.write('      <ele>{:.2f}</ele>\n'.format(ele))
        f.write('      <time>{}</time>\n'.format(now))
        f.write('      <extensions><speed>{:.2f}</speed></extensions>\n'.format(speed))
        f.write('    </trkpt>\n')

def close_gpx():
    with open(gpx_path, 'a') as f:
        f.write('  </trkseg></trk>\n</gpx>\n')

def gps_logger(stop_event):
    gpsd.connect()
    while not stop_event.is_set():
        try:
            packet = gpsd.get_current()
            if packet.mode >= 2:
                lat = packet.lat
                lon = packet.lon
                ele = packet.alt if packet.alt else 0.0
                speed = packet.hspeed if packet.hspeed else 0.0
                append_gpx(lat, lon, ele, speed)
        except:
            pass
        time.sleep(1)

def record_audio(duration=60):
    print("🎙 開始錄音與 GPS 紀錄... 錄製 {} 秒".format(duration))
    cmd = ["arecord", "-D", "plughw:1,0", "-f", "S16_LE", "-r", "96000", "-c", "1", "-d", str(duration), wav_path]
    subprocess.run(cmd)

if __name__ == "__main__":
    os.makedirs(output_dir, exist_ok=True)
    init_gpx()
    stop_event = threading.Event()
    gps_thread = threading.Thread(target=gps_logger, args=(stop_event,))
    gps_thread.start()

    try:
        record_audio(duration=60)
    except KeyboardInterrupt:
        print("\n🛑 偵測到 Ctrl+C，結束錄音與 GPS")
    finally:
        stop_event.set()
        gps_thread.join()
        close_gpx()
        print("✅ 錄音與 GPX 儲存完成！")
