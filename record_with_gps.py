import os
import time
import subprocess
from datetime import datetime

# 建立 logs 資料夾
output_dir = os.path.expanduser("~/AcousticGPS/logs")
os.makedirs(output_dir, exist_ok=True)

# 時間戳記
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
wav_path = os.path.join(output_dir, f"record_{ts}.wav")
gpx_path = os.path.join(output_dir, f"record_{ts}.gpx")

# 啟動 GPS 紀錄
gps_cmd = [
    "gpspipe", "-w", "-o", gpx_path
]
gps_proc = subprocess.Popen(gps_cmd)
print("🛰️ GPS 紀錄啟動")

# 等待 GPS 穩定
time.sleep(3)

# 啟動錄音（stderr 捕捉）
rec_cmd = [
    "arecord", "-D", "plughw:0,0",
    "-f", "S16_LE", "-r", "96000", "-c", "1",
    "-d", "60", wav_path
]
print("🎙️ 錄音開始")
rec_proc = subprocess.run(rec_cmd, capture_output=True, text=True)

# 停止 GPS
gps_proc.terminate()
print("🛑 錄音與 GPS 結束")

# 儲存 arecord 訊息
with open(os.path.join(output_dir, f"log_{ts}.txt"), "w") as f:
    f.write(rec_proc.stdout)
    f.write("\n")
    f.write(rec_proc.stderr)

# 檢查錄音結果
if os.path.exists(wav_path):
    size = os.path.getsize(wav_path)
    if size <= 44:
        print(f"❌ 錄音失敗：檔案僅有 Header（{size} bytes）")
        print("🔎 請確認錄音裝置是否接好，或使用 arecord 手動測試")
    elif size < 1000:
        print(f"⚠️ 錄音異常，檔案過小：{size} bytes，請檢查錄音裝置或驅動")
    else:
        print(f"✅ 錄音與 GPX 儲存完成：{size} bytes")
else:
    print("❌ 錄音失敗，無檔案")